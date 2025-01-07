// Import required packages
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const promClient = require('prom-client');
const { body, validationResult } = require('express-validator');

// Create Express app
const app = express();

// Prometheus metrics setup
const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

// Custom metrics
const customerRequests = new promClient.Counter({
  name: 'customer_service_requests_total',
  help: 'Total number of requests to customer service',
  labelNames: ['method', 'endpoint', 'status'],
  registers: [register]
});

const customerLatency = new promClient.Histogram({
  name: 'customer_service_latency_seconds',
  help: 'Time taken to process customer requests',
  labelNames: ['method', 'endpoint'],
  registers: [register]
});

// MongoDB connection config
const MONGO_URI = 'mongodb://mongo:27017';
const DB_NAME = 'crm-project';
const COLLECTION_NAME = 'customers';

// Customer Schema
const customerSchema = new mongoose.Schema({
  customer_id: String,
  name: { type: String, required: true },
  email: { type: String, required: true },
  phone: { type: String, required: true },
  address: { type: String, required: true },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now }
});

const Customer = mongoose.model('Customer', customerSchema);

// Middleware
app.use(express.json());
app.use(cors());

// Metrics middleware
const metricsMiddleware = (method, endpoint) => async (req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    customerRequests.labels(method, endpoint, res.statusCode.toString()).inc();
    customerLatency.labels(method, endpoint).observe(duration / 1000);
  });
  next();
};

// Routes
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Get all customers with pagination
app.get('/api/customers', metricsMiddleware('GET', '/customers'), async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    const customers = await Customer.find()
      .sort({ created_at: -1 })
      .skip(skip)
      .limit(limit);

    res.json({ status: 'success', data: customers });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get customer by customer_id
app.get('/api/customers/:id', metricsMiddleware('GET', '/customers/:id'), async (req, res) => {
  try {
    const customer = await Customer.findOne({ customer_id: req.params.id });
    if (!customer) {
      return res.status(404).json({ error: 'Customer not found' });
    }
    res.json({ status: 'success', data: customer });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Add a new customer
app.post('/api/customers', 
  metricsMiddleware('POST', '/customers'),
  [
    body('name').notEmpty(),
    body('email').isEmail(),
    body('phone').notEmpty(),
    body('address').notEmpty()
  ],
  async (req, res) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }

      const customer = new Customer({
        customer_id: 'CUST' + Math.floor(Math.random() * 1000),
        ...req.body,
        created_at: new Date(),
        updated_at: new Date()
      });

      await customer.save();
      res.status(201).json({ status: 'success', message: 'Customer added successfully' });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
);

// Connect to MongoDB and start server
const startServer = async () => {
  try {
    await mongoose.connect(`${MONGO_URI}/${DB_NAME}`);
    console.log('Connected to MongoDB');

    const PORT = process.env.PORT || 8085;
    app.listen(PORT, () => {
      console.log(`Customer service starting on :${PORT}`);
    });
  } catch (error) {
    console.error('Failed to connect to MongoDB:', error);
    process.exit(1);
  }
};

startServer();

module.exports = app; // For testing purposes