def calculate_subtotal(price, quantity):
    return price * quantity

def calculate_discount(subtotal, discount_percent):
    return subtotal * discount_percent / 100

def calculate_final_price(subtotal, discount_amount):
    return subtotal - discount_amount

def classify_lead(budget):
    if budget >= 40000:
        return "Premium Lead"
    elif budget >= 25000:
        return "Qualified Lead"
    else:
        return "Low Budget Lead"


for i in range(1, 4):
    
    
    customer_name = input(f"Enter Customer {i} Name: ")
    product_name = input(f"Enter Product {i} Name: ")
    unit_price = float(input(f"Enter Unit Price : "))
    quantity = int(input(f"Enter Quantity : "))
    discount_percent = float(input(f"Enter Discount%: "))
    budget = float(input(f"Enter Customer Budget : "))

    subtotal = calculate_subtotal(unit_price, quantity)
    discount_amount = calculate_discount(subtotal, discount_percent)
    final_price = calculate_final_price(subtotal, discount_amount)
    lead_status = classify_lead(budget)

    print("===== ULTIMA SALES CALCULATOR =====")
    print(f"Customer:    {customer_name}")
    print(f"Product:     {product_name}")
    print(f"Unit Price:  BDT {unit_price:,.2f}")
    print(f"Subtotal:    BDT {subtotal:,.2f}")
    print(f"Discount:    BDT {discount_amount:,.2f}")
    print(f"Final Price: BDT {final_price:,.2f}")
    print(f"Lead Status: {lead_status}")
    