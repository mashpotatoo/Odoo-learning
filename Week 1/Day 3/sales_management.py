class Product:
    def __init__(self, name , price):
        self.name = name
        self.price = price
    def show_info(self):
        print(f"Product: {self.name}")
        print(f"Price: BDT {self.price:,.2f}")

class WaterPurifier(Product):
    def __init__(self, name, price, capacity):
        super().__init__(name, price)
        self.capacity = capacity
    def show_info(self):
        super().show_info()
        print(f"Capacity: {self.capacity}")
        print()
    def calculate_discount(self,discount):
        
        discount_price = self.price * discount / 100
        final_price = self.price - discount_price
        return final_price
    


        



p1 = Product("Trishield", 35000)
p2 = Product("Crystal RO",25000)
p1.show_info()
p2.show_info()

p3 = WaterPurifier("TriShield",35000,15)
p3.show_info()

class Product:
    def __init__(self, name , price):
        self.name = name
        self.price = price
    def show_info(self):
        print(f"Product: {self.name}")
        print(f"Price: BDT {self.price:,.2f}")

class WaterPurifier(Product):
    def __init__(self, name, price, capacity):
        super().__init__(name, price)
        self.capacity = capacity
    def show_info(self):
        super().show_info()
        print(f"Capacity: {self.capacity}")
        print()
    def calculate_discount(self,discount):
        
        discount_price = self.price * discount / 100
        final_price = self.price - discount_price
        return final_price
class Lead:
    def __init__(self, name, budget,interested_product):
        self.name = name
        self.budget = budget
        self.interested_product = interested_product
    def classify(self):
        if self.budget  >= 40000:
            return("Premium Lead")
        elif self.budget >= 25000:
            return("Qualified Lead")
        else:
            return("Low Budget Lead")
    def show_info(self):
        print(f"Name: {self.name}")
        print(f"Budget: BDT {self.budget:,.2f}")
        print(f"Interested Product: {self.interested_product}")
        print(f"Status: {self.classify()}")

    


        



p1 = Product("Trishield", 35000)
p2 = Product("Crystal RO",25000)
p1.show_info()
p2.show_info()

p3 = WaterPurifier("TriShield",35000,15)
p3.show_info()

result = p3.calculate_discount(10)

print(f"Final Price: BDT {result:,.2f}")
p4 = Lead("Rahim", 40000, "TriShield")
lead_status = p4.classify()
print(lead_status)
p4.show_info()