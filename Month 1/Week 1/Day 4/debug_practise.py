class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def calculate_discount(self, discount):
        discount_amount = self.price * discount / 100
        final_price = self.price - discount_amount
        return final_price


product = Product("TriShield", 35000)

result = product.calculate_discount(10)

print(f"Product: {product.name}")
print(f"Final Price: BDT {result:,.2f}")