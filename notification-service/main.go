package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

type Order struct {
	OrderID    string  `json:"order_id"`
	CustomerID string  `json:"customer_id"`
	Items      []Item  `json:"items"`
	TotalPrice float64 `json:"total_price"`
	Status     string  `json:"status"`
	CreatedAt  string  `json:"created_at"`
}

type Item struct {
	ProductName string  `json:"product_name"`
	Quantity    int     `json:"quantity"`
	Price       float64 `json:"price"`
}

func handleOrder(w http.ResponseWriter, r *http.Request) {
	// Decode the order from the request body
	var order Order
	if err := json.NewDecoder(r.Body).Decode(&order); err != nil {
		http.Error(w, "Invalid order data", http.StatusBadRequest)
		return
	}

	// Print the received order
	fmt.Printf("Received Order: %+v\n", order)

	// Send a 200 OK response
	w.WriteHeader(http.StatusOK)
}

func main() {
	// Setup HTTP server to listen for incoming orders
	http.HandleFunc("/orders", handleOrder)

	// Start the HTTP server
	port := "5001"
	fmt.Printf("Order Subscriber listening on port %s...\n", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}
