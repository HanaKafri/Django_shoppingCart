'''
The backend component is responsible for implementing the core functionality of your 
application, such as validating user input, performing calculations, and enforcing business rules. 

The backend component can be organized into different modules or apps, 
each with its own models, views, and urls. 
The models define the data structures and relationships for your application,
the views handle the requests and responses, 
and the urls map the endpoints to the views.

'''


from .repository import CategoryRepository

# calls repository to create a category, and returns the created category
class CategoryComponent:
    def __init__(self, session):
        self.category_repository = CategoryRepository(session)

    def create_category(self, category_data):
        return self.category_repository.create_category(category_data)
