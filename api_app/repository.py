

'''

The repository component is responsible for managing the persistence 
and retrieval of data from the database. 

The repository component can use the built-in ORM (object-relational mapper) of Django, 
which allows you to query and manipulate data using Python objects and methods. 
The repository component can also use custom SQL queries or raw SQL statements if needed.

'''

from .models import Category  # Assuming you have a Category model defined


# access database
class CategoryRepository:
    def __init__(self, session):
        self.session = session

    def create_category(self, category_data):
        new_category = Category(**category_data) #param: name=name
        self.session.add(new_category)
        self.session.commit()
        return new_category

