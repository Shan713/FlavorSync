import datetime as dt
from seasonal_menu_items import *
import sys
"""
    The User class represents a user in the system, storing details like their name, password, address, favorite cuisine, and dietary preferences.
    It also keeps track of the user's order history and allergens, ensuring that their preferences are considered when recommending food items.
"""
class User:
    def __init__(self, name, password, address, fav_cuisine, dietary_pref,allergens):
        self.name = name
        self.password = password
        self.address = address
        self.fav_cuisine = fav_cuisine
        self.dietary_pref = dietary_pref
        self.order_history = []  # Foods the user has ordered/liked
        self.allergens = allergens if allergens is not None else []  # List of allergens
        self.ratings ={}
"""
    The Food class represents a food item, storing information like the name, cuisine type, nutritional details, and restrictions.
    It also includes additional attributes like allergens, meal type, and flavor profile for more personalized recommendations.
"""
class Food:
    def __init__(self, name, cuisine_type,calories,nutrition_score,dietary_restrictions, allergens, meal_type, flavor_profile):
        self.name = name
        self.cuisine_type = cuisine_type
        self.calories = calories
        self.nutrition_score = nutrition_score
        self.rating = 0
        self.dietary_restrictions = dietary_restrictions
        self.allergens = allergens
        self.meal_type = meal_type
        self.flavor_profile = flavor_profile
        self.timestamp = 0
        self.promotion = None
class FoodNodeDLL:
    """
    Node class for Doubly Linked List to track new food arrivals.
    Each node maintains references to previous and next nodes for
    bidirectional traversal.
    """
    def __init__(self, food):
        self.food = food
        self.prev = None
        self.next = None

class DoublyLinkedList:
    """
    Maintains most recent food additions with automatic removal of oldest items.
    """
    def __init__(self, max_size=5):
        self.head = None
        self.tail = None
        self.size = 0
        self.max_size = max_size
    
    def append(self, food):
        """
        Add new food item to list, removing oldest if at capacity.
        Time Complexity: O(1)
        """
        if self.size >= self.max_size:
            # Remove oldest item
            self.head = self.head.next
            if self.head:
                self.head.prev = None
            self.size -= 1
            
        new_node = FoodNodeDLL(food)
        if not self.head:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self.size += 1

    def get_new_arrivals(self):
        """
        Retrieve list of most recent food items.
        It returns List of food names, ordered from newest to oldest
        Time Complexity: O(k) where k is max_size
        """
        arrivals = []
        current = self.tail  # Start from the recent one
        count = 0
        while current and count < self.max_size:
            arrivals.append(current.food.name)
            current = current.prev
            count += 1
        return arrivals
class MaxHeap:
    """
    MaxHeap data structure for maintaining dishes sorted by rating.It used for the efficient retrieval 
    of highest rated dishes
    """
    def __init__(self):
        self.heap = []

    def push(self, dish):
        """
        Add new dish to heap and maintain heap property.
        Time Complexity: O(log n)
        """
        self.heap.append(dish)
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        """
        Remove and return highest rated dish from heap.
        It returns the Food object with highest rating or None if heap is empty
        Time Complexity: O(log n)
        """
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        # Store root (highest rated) and move last element to root
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)# Restore heap property
        return root

    def _heapify_up(self, index):
        while index > 0:
            parent_index = (index - 1) // 2
            # If current element has higher rating than parent, swap them
            if self.heap[index].rating > self.heap[parent_index].rating:
                self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
                index = parent_index
            else:
                break

    def _heapify_down(self, index):
        child_index = 2 * index + 1
        while child_index < len(self.heap):
            right_child_index = child_index + 1
            # Find the child with higher rating
            if (right_child_index < len(self.heap) and self.heap[right_child_index].rating > self.heap[child_index].rating):
                child_index = right_child_index

            if self.heap[index].rating < self.heap[child_index].rating:
            # If current element has lower rating than child, swap them
                self.heap[index], self.heap[child_index] = self.heap[child_index], self.heap[index]
                index = child_index
            else:
                break
class CuisineTrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_cuisine = False


class CuisineTrie:
    """
    A node class for the Cuisine Trie data structure that efficiently stores and retrieves cuisine names.
    Each node represents a character in a cuisine name and maintains references to its child nodes.
    """
    def __init__(self):
        self.root = CuisineTrieNode()

    def insert(self, cuisine):
        """
        Insert a new cuisine name into the trie.
        Traverses the trie character by character, creating new nodes as needed.
        If a character doesn't exist in the current node's children, creates a
        new node for that character. Marks the last node as the end of a cuisine name.
        """
        node = self.root
        for char in cuisine:
            if char not in node.children:
                node.children[char] = CuisineTrieNode()
            node = node.children[char]
        node.is_end_of_cuisine = True

    def search(self, cuisine):
        """
        Search for a complete cuisine name in the trie.Traverses the trie character by character 
        to find the given cuisine.Returns True only if the exact cuisine name exists and is marked as
        a complete cuisine name.
        """
        node = self.root
        for char in cuisine:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_cuisine

"""
NutritionTree is a BST in which the criteria is the nutrition score obtained during the addition of food item. Based on the nutrition score the food items are
ordered just like in a BST. This is used to retrieve food item faster based on the nutrition score.
It has a Node which contains a food node and left and right pointers. The root node is initialised to none in the beginning.
"""
class NutritionTree:
    def __init__(self):
        self.root = None

    class Node:
        def __init__(self, food):
            self.food = food
            self.left = None
            self.right = None

    """
    The insert_food method inserts the NutritionTree node based on the nutrition score i.e node.food.nutrition_score.
    The helper function _insert recursively works to insert the given node.    
    """
    def insert_food(self, food):
        if self.root is None:
            self.root = self.Node(food)
        else:
            self._insert(self.root, food)

    def _insert(self, node, food):
        if food.nutrition_score < node.food.nutrition_score:
            if node.left is None:
                node.left = self.Node(food)
            else:
                self._insert(node.left, food)
        else:
            if node.right is None:
                node.right = self.Node(food)
            else:
                self._insert(node.right, food)
    """
    The modified version of inOrder traversal is used to give the recommendations based on the nutrition score, this basically returns food items that are
    more are less similar in nutrition score i.e cousins or siblings in the tree.
    """

    def inorder_recommendations(self, avg_score, tolerance):
        recommendations = []

        def _inorder(node):
            if node is not None:
                _inorder(node.left)
                
                # Check if the food's nutrition score is within the specified range
                if avg_score - tolerance <= node.food.nutrition_score <= avg_score + tolerance:
                    recommendations.append(node.food.name)
                
                _inorder(node.right)
        
        _inorder(self.root)
        return recommendations
    """This method searches for a food item with a specified nutrition score in the tree.
    If an exact match is found, it returns the food's name.
    If no exact match is found, it returns the next closest food with a lower nutrition score."""
    def get_food(self, nutrition_score):
        closest_food = None

        result = self._search(self.root, nutrition_score, closest_food)
        return result if result is not None else closest_food
    
    """This helper function performs a recursive search through the NutritionTree.
    It checks each node for an exact match to the given nutrition score.
    If no match is found, it keeps track of the closest food while continuing the search."""
    def _search(self, node, nutrition_score, closest_food):
        if node is None:
            return closest_food
        if node.food.nutrition_score == nutrition_score:
            return node.food.name
        elif nutrition_score < node.food.nutrition_score:
            return self._search(node.left, nutrition_score, closest_food)
        else:
            return self._search(node.right, nutrition_score, node.food.name)
    
"""
The graph is the basic data structure in this Food recommendation system as the relationship between a user and food node is established by means of an edge.

The graph class has three methods:
    i)add_vertex -> this method adds vertex (either user or food) by creating a key in the adj list of the graph.
    ii)add_edge -> this method adds the vertex in both key's value by appending vice-versa in the adj list of the graph.
    iii) print_graph -> this methods prints the Vertex and its neighbours. This method is just for verifying the working of the code.
"""

class Graph:
    def __init__(self):
        self.adj_list = {}

    def add_vertex(self, vertex):
        if vertex not in self.adj_list:
            self.adj_list[vertex] = []
            return True
        return False

    def add_edge(self, v1, v2):
        if v1 in self.adj_list and v2 in self.adj_list:
            self.adj_list[v1].append(v2)
            self.adj_list[v2].append(v1)
            return True
        return False

    def print_graph(self):
        for vertex in self.adj_list:
            print(vertex, ":", self.adj_list[vertex])

class OfferNode:
    def __init__(self,food):
        self.food = food
        self.left = None
        self.right = None

class OfferBST:
    def __init__(self):
        self.root = None

    def insert_offer_BST(self,food):
        new_node = OfferNode(food)
        if self.root is None:
            self.root = new_node
            return
        current = self.root
        while True:
            if new_node.food.name < current.food.name:
                if current.left is None:
                    current.left = new_node
                    return
                else:
                    current = current.left
            elif new_node.food.name > current.food.name:
                if current.right is None:
                    current.right = new_node
                    return
                else:
                    current = current.right

    """The in order traversal allows the lexicographical arrange of the food names"""

    def in_order_offer(self):
        offers = []
        self._in_order_offer(self.root, offers)
        return offers

    def _in_order_offer(self, node, offers):
        if node is None:
            return
        self._in_order_offer(node.left, offers)
        offers.append(node.food)
        self._in_order_offer(node.right, offers)

"""
The RecommendationSystem class has attributes such as users(list of users in the system),food_items (list of food items in the system), logged_user (maintains the current logged in user),
graph (the graph which has the relationships between user and food for the system), nutritionTree (the nutritionTree which stores the food nodes based on nutrition score), popular_dishes (a dictionary
which stores the food_name : count of the food_ordered) and available_restritions
The methods in this class serves as the important functions which interact with user and provide outputs which recommends food to the user.
"""
class RecommendationSystem:
    def __init__(self):
        self.users = []
        self.food_items = []
        self.logged_user = None  # Store the current logged in user
        self.graph = Graph()
        self.nutritionTree = NutritionTree() 
        self.popular_dishes = {}
        self.available_restrictions = ["Gluten-Free", "Nut-Free", "Dairy-Free", "Vegan", "Vegetarian"]
        self.cuisine_trie = CuisineTrie()  # Trie for cuisines
        self.cuisines = {}  # cuisine_type: List of Dishes
        self.new_arrivals = DoublyLinkedList()
        self.promotion_list = []

    """The adduser methods gets arguements such as name,password,address,fav cuisine and dietary preferences and checks the existence of user by name. If no user exists with the name, specific
    allergens will be collected from the user and then these arg are passed to the constructor of the user node and a new node is created. After the creation, a new vertex is added in the graph and the user list is appended with the new
    user."""
    def addUser(self,temp_name, temp_pass, temp_address, temp_fav_cuisine, temp_dietary_pref):
        for name in self.users:
            if (name==temp_name):
                print("Username already exists. Try again!")
                return
        temp_allergens = "None"
        new_user = User(temp_name, temp_pass, temp_address, temp_fav_cuisine, temp_dietary_pref,temp_allergens)
        self.users.append(new_user)
        self.graph.add_vertex(new_user)
        print(f"{temp_name} is added successfully!\n")
    
    """
    This list_users function iterates throught the user list i.e self.user to print all user's details. This method is just for verifying the working of the code. 
    """
    def list_users(self):
        if not self.users:
            print("No users in the system.\n")
        else:
            for user in self.users:
                print(f"User: {user.name}, Address: {user.address}, Favorite Cuisine: {user.fav_cuisine}, Dietary Preferences: {user.dietary_pref}, Allergens: {user.allergens}")
    """
    The addFood function allows administrators to add new food items to the system. 
    It first checks if a food item with the given name already exists in the system. If it exists, the function aborts the addition to prevent duplicates.
    If the food is new, the function calculates a nutrition score using the provided nutritional information.
    The new food is then added to both the list of food items and the graph, as well as the nutrition tree for quick lookups by nutritional value.
    The method also ensures that food is associated with any dietary restrictions and allergens.
    """
    def addFood(self,temp_name,temp_cuisine_type,temp_calories,temp_proteins,temp_fats,temp_carbohydrates,temp_vitamins,temp_minerals,temp_dietary_restrictions,temp_allergens,temp_meal_type,temp_flavor_profile):
        # Check if food already exists
        for food in self.food_items:
            if food.name == temp_name:
                print("Food item already exists. Try again!\n")
                return
        #calculate nutrition score    
        temp_score = self.nutrition_score(temp_calories,temp_proteins,temp_fats,temp_carbohydrates,temp_vitamins,temp_minerals)
        new_food = Food(temp_name,temp_cuisine_type,temp_calories,temp_score,temp_dietary_restrictions,temp_allergens,temp_meal_type,temp_flavor_profile)
        #Cuisine based reco 
        if temp_cuisine_type in self.cuisines:
            new_food.timestamp = len(self.cuisines[temp_cuisine_type])
            self.cuisines[temp_cuisine_type].append(new_food)
            self.new_arrivals.append(new_food)
        else:
            print(f"Warning: Cuisine type '{temp_cuisine_type}' not found in system. Food item will not be available for cuisine-based recommendations.\n")

        self.food_items.append(new_food)
        self.graph.add_vertex(new_food)
        self.nutritionTree.insert_food(new_food)
        
        print(f"{new_food.name} added succesfully!\n")
    
    """
    The login_user function handles user authentication by prompting the user for their username and password.
    It iterates through the user list to find the matching username. If the username exists, it checks whether the provided password is correct.
    If the login is successful, the function logs in the user and stores the logged-in user as self.logged_user for future actions like ordering food or getting recommendations.
    If either the username is not found or the password is incorrect, it provides appropriate feedback to the user.
    """
    def login_user(self):
        temp_name = input("Enter your username: ")
        temp_pass = input("Enter your password: ")
        
        #Find the user in the system
        for user in self.users:
            if user.name == temp_name:
                # check password
                if temp_pass == user.password:
                    print(f"User {temp_name} logged in successfully!")
                    self.logged_user = user  # Store the logged-in user for future purpose like for recommending for the logged in user.
                    return True
                else:
                    print("Invalid password.")
                    sys.exit()
                    return False
        
        print(f"User '{temp_name}' not found.")
        sys.exit()
        return False
    """
    The order_food function allows a logged-in user to place an order for a specific food item.
    It checks if the user is logged in, then searches for the specified food item by name.
    If the food item exists, an edge is added between the user and the food in the graph to track the relationship.
    The user's order history is updated, and the system tracks the popularity of food items based on the number of times they are ordered.
    If the food item is not found, the function informs the user.
    """
    def order_food(self,food_name,quantity):
        if not self.logged_user:
            print("User not logged in.")
            return
        for food in self.food_items:
            if food.name == food_name:
                self.graph.add_edge(self.logged_user,food)
                self.logged_user.order_history.append((food_name,quantity))

                # Update the count of ordered food for popularity
                if food_name in self.popular_dishes:
                    self.popular_dishes[food_name] += quantity
                else:
                    self.popular_dishes[food_name] = quantity

                print(f"Food ordered: {self.logged_user.name} Ordered {food_name},Quantity: {quantity}")
                return
        
        print(f"Food item '{food_name}' not found.")

   
    # This method allows the currently logged-in user to update their dietary preferences and allergens.
    # It first displays the current preferences, then takes user input for new preferences and allergens
    # and updates the user’s information accordingly.
    def update_user_dietary_preferences(self):
        if not self.logged_user:
            print("User not logged in.")
            return
        
        print(f"Current dietary preferences: {self.logged_user.dietary_pref}")
        new_pref = input("Enter new dietary preferences (comma-separated): ")
        self.logged_user.dietary_pref = new_pref

        print(f"Current allergens: {self.logged_user.allergens}")
        new_allergens = self.get_allergens()
        self.logged_user.allergens = new_allergens
        
        print("Dietary preferences and allergens updated successfully.")
    
    # This helper method prompts the user to input dietary restrictions from a pre-defined list.
    # It continuously displays the list of available restrictions and collects the user’s choices until they are done.
    def get_dietary_restrictions(self):
        restrictions = []
        while True:
            print("Available dietary restrictions:")
            for idx, restriction in enumerate(self.available_restrictions):
                print(f"{idx + 1}. {restriction}")
            choice = input("Select dietary restrictions by number (or type 'done' to finish): ")
            if choice.lower() == 'done':
                break
            if choice.isdigit() and 0 < int(choice) <= len(self.available_restrictions):
                restrictions.append(self.available_restrictions[int(choice) - 1])
            else:
                print("Invalid choice. Please try again.")
        return restrictions
    
    # Provides a list of complementary dishes based on the selected main dish, considering cuisine type and flavor profile.
    def pair_recommendations(self, main_dish_name):
        if not self.logged_user:
            print("User not logged in.")
            return []

        complementary_dishes = []
        selected_main_dish = None

        # Find the main dish in food_items
        for food in self.food_items:
            if food.name == main_dish_name:
                selected_main_dish = food
                break
        
        if not selected_main_dish:
            print(f"Main dish '{main_dish_name}' not found.")
            return []

        # Recommend complementary dishes based on cuisine type and flavor profile
        for food in self.food_items:
            if food.name != main_dish_name:
                # Simple logic: Suggest dishes of the same cuisine type or compatible flavor profiles
                if food.cuisine_type == selected_main_dish.cuisine_type or food.flavor_profile==selected_main_dish.flavor_profile:
                    complementary_dishes.append(food.name)

        if complementary_dishes:
            print(f"Complimentary Dishes for {main_dish_name}")
            return self.print_recommendations(complementary_dishes)
        else:
            print(f"No pairing recommendations found for {main_dish_name}.")
            return []

    
    def add_cuisine(self, cuisine):
        self.cuisine_trie.insert(cuisine)
        self.cuisines[cuisine] = []
    
    def rate_dish(self,cuisine, dish_name, rating):
        if  self.cuisine_trie.search(cuisine):
            self.logged_user.ratings[dish_name] = rating
            
            # Update the rating in the dish list
            for food in self.cuisines.get(cuisine,[]):
                if food.name == dish_name:
                    food.rating = rating
                    print(f"Rated {dish_name} with {rating} in {cuisine}.")
                    return
            print(f"Dish '{dish_name}' not found in cuisine '{cuisine}'.")
        else:
            print(f"Cuisine '{cuisine}' not found in the system.")

    def cuisine_based_recommendations(self, cuisine):
        #Validate cuisine exists
        if not self.cuisine_trie.search(cuisine):
            print(f"Cuisine '{cuisine}' not found in the system.")
            return []
        #Check if cuisine has dishes
        if cuisine not in self.cuisines or not self.cuisines[cuisine]:
            print(f"No dishes found for cuisine '{cuisine}'.")
            return []

        # Use MaxHeap to get top rated dishes
        max_heap = MaxHeap()
        for food in self.cuisines[cuisine]:
            max_heap.push(food)

        # Collect dishes sorted by rating (highest to lowest)
        print(f"Top Rated {cuisine} Dishes:")
        top_dishes = []
        while len(max_heap.heap) > 0:
            dish = max_heap.pop()
            top_dishes.append(dish.name)
        return self.print_recommendations(top_dishes)
        
    def get_new_arrivals(self):
        """
        Retrieve most recently added dishes.
        It return the List of dish names ordered from newest to oldest
        Time Complexity: O(k) where k is max size of new arrivals list
        """
        #Initialize result collection
        arrivals = []
        current = self.new_arrivals.tail  # Start from most recent
        #Handle empty case
        if self.new_arrivals.size == 0:
            return []
        #Collect recent arrivals up to max size
        while current and len(arrivals) < self.new_arrivals.max_size:
            arrivals.append(current.food.name)
            current = current.prev
        
        return self.print_recommendations(arrivals)
    
    """
    The personalized_recommendations function generates food recommendations for the logged-in user based on their previous orders.
    It checks the logged-in user's connections (edges) in the graph to suggest food items they have already ordered.
    If no orders are found, it attempts to recommend items ordered by other users. If recommendations are still not found, it falls back to time-based suggestions.
    The function returns a list of up to 5 food items as recommendations.
    """
    def personalized_recommendations(self):
        if not self.logged_user:
            print("User not logged in.")
            return []
        recommendations = []
        if self.logged_user in self.graph.adj_list and self.graph.adj_list[self.logged_user]:
            for food in self.graph.adj_list[self.logged_user]:
                if food.name not in recommendations:
                    recommendations.append(food.name)
    
        if not recommendations:
            print(f"No orders found for user '{self.logged_user.name}'. Recommending from other users.")
            for user in self.users:
                if user != self.logged_user and user in self.graph.adj_list:
                    for food in self.graph.adj_list[user]:
                        if food.name not in recommendations:
                            recommendations.append(food.name)
    
    # Cold case handling: if still no recommendations, use any of the other reco methods
        if not recommendations:
            return self.time_based_suggestions()
        if recommendations:
            print(f"{self.logged_user.name}'s Personalised Recommendations: ")
        return self.print_recommendations(recommendations[:5])  # Return up to 5 recommendations

    """
    The Nutrition score methods acts as a helper method for building a BST based on this nutrition scores. 
    This functions takes all the attributes related to the nutrition of the food from the food node and calculates a
    score called nutrition score (own calculation formula) which helps in differentiating the food based on nutrition.
    """
    def nutrition_score(self, calories,proteins,fats,carbs,vitamins,minerals):
        # Base score calculation using macronutrients
        score = (proteins * 4) + (fats * 9) + (carbs * 4) - (calories * 0.1)
        # Vitamins and minerals contribute positively
        score += len(vitamins) * 2  # Each vitamin adds 
        score += len(minerals) * 1.5  # Each mineral adds
        return score
    """
    The recommend_based_on_nutrition function generates food recommendations for the logged-in user based on their average nutritional score.
    It first calculates the average nutrition score of the foods the user has previously ordered, which are accessible through the edges in the graph.
    If the user has not ordered any food yet, it notifies them and returns an empty list.
    Once the average score is calculated, it queries the nutritionTree to find food items with similar nutritional values.
    then the function prints the top recommendations using the print_recommendations function.
    """
    def recommend_based_on_nutrition(self):
        total_Score = 0
        count = 0
        for food in self.graph.adj_list[self.logged_user]:
            total_Score+=food.nutrition_score
            count+=1
        if count==0:
            print("No food ordered yet to calculate average nutrition score.")
            return []
        avg_score = total_Score/count

        recommendations = self.nutritionTree.inorder_recommendations(avg_score,15)
        if recommendations:    
            print("Nutrition based recommendations: ")
        return self.print_recommendations(recommendations)
    
    """This method searches for a food item with a specified nutrition score in the tree.This calls a function in the NutritionTree class which
    fetches the food with its nutrition score.."""
    def get_food_based_on_nutrition(self,nutritionScore):
        return self.nutritionTree.get_food(nutritionScore)
    """
    The print_recommendations function takes in a list of recommended food items and displays them for the logged-in user.
    If there are no recommendations available, it notifies the user. When there are recommendations, the function formats and prints them, numbering each item.
    """
    def print_recommendations(self, recommendations):
        if not recommendations:
            print("No recommendations available.")
            return

        print(f"\n{'-'*40}\nTop Recommendations for {self.logged_user.name}:\n{'-'*40}")
        for i, food_name in enumerate(recommendations, 1):
            print(f"{i}. {food_name}")
        print(f"{'-'*40}\n")
    
    # Preamble for Popular Dishes
    # Popular dishes recommendation is based on user order history.
    # We maintain a hash map (dictionary) where the key is the food item and the value is the count of times it has been ordered.
    # Time complexity:
    # - Insertion/Update of orders is O(1) as hash maps offer constant time insertion and updates.
    # - To find the most popular dishes, we sort the hash map based on order count (O(n log n), where n is the number of unique food items ordered).
    # - Retrieving the top 5 most popular dishes is O(1) after sorting.

    def popular_dishes_recommendation(self):
        # Sort the popular dishes by the number of orders and return the top 5
        sorted_dishes = sorted(self.popular_dishes.items(), key=lambda x: x[1], reverse=True)
        popular_recommendations = [dish[0] for dish in sorted_dishes[:5]]
        return self.print_recommendations(popular_recommendations)
    
    # Preamble for Time-Based Suggestions
    # Time-based suggestions recommend food items based on the current time of day.
    # The system categorizes food by meal type (Breakfast, Lunch, Dinner), and provides recommendations accordingly.
    # Time complexity:
    # - Determining the meal type based on the current hour is O(1).
    # - Filtering the food items based on meal type is O(m), where m is the number of available food items.

    def time_based_suggestions(self):
        current_hour = dt.datetime.now().hour
        current_day = dt.datetime.now().weekday()  # 0 is Monday, 6 is Sunday
        meal_suggestions = []
        quick_meal_calories = 500  # Threshold for a quick meal

        if current_day < 5:  # Weekdays (Monday to Friday)
            if 6 <= current_hour < 11:  # Breakfast
                meal_suggestions = [food.name for food in self.food_items if food.meal_type.lower() == "breakfast" and food.calories < quick_meal_calories]
            elif 11 <= current_hour < 17:  # Lunch
                meal_suggestions = [food.name for food in self.food_items if food.meal_type.lower() == "lunch" and food.calories < quick_meal_calories]
            elif 17 <= current_hour < 22:  # Dinner
                meal_suggestions = [food.name for food in self.food_items if food.meal_type.lower() == "dinner" and food.calories < quick_meal_calories]
            else:  # Late-night snacks
                meal_suggestions = [food.name for food in self.food_items if food.meal_type.lower() in ["snack", "late-night"] and food.calories < quick_meal_calories]
        else:  # Weekends (Saturday and Sunday)
            if 6 <= current_hour < 11:  # Breakfast
                meal_suggestions = [food.name for food in self.food_items if food.meal_type.lower() == "breakfast"]
            elif 11 <= current_hour < 17:  # Lunch
                meal_suggestions = [food.name for food in self.food_items if food.meal_type.lower() == "lunch"]
            elif 17 <= current_hour < 22:  # Dinner
                meal_suggestions = [food.name for food in self.food_items if food.meal_type.lower() == "dinner"]
            else:  # Late-night snacks
                meal_suggestions = [food.name for food in self.food_items if food.meal_type.lower() in ["snack", "late-night"]]

        return self.print_recommendations(meal_suggestions[:5])  # Return up to 5 meal suggestions

    def add_offers(self,food_name,offer):
        for food in self.food_items:
            if food.name == food_name:
                food.promotion = offer
                self.promotion_list.append(food)
                return
        print("Food not found")
        return

    def offer_recommendation(self):
        offer_tree = OfferBST()
        for offer in self.promotion_list:
            offer_tree.insert_offer_BST(offer)
        ascending_order = offer_tree.in_order_offer()
        print("-----------------------------------------------------------------------------------")
        print("Special Offers!!!!!")
        for offer in ascending_order:
            print(f"Food name: {offer.name},Cuisine type: {offer.cuisine_type},Offer: {offer.promotion}.")
        print("-----------------------------------------------------------------------------------")
    
    def logout(self):
        self.logged_user = None


def main():
    recommendation_system = RecommendationSystem()
    seasonal_menu=SeasonalMenu()
    recommendation_system.addUser("Gopal", "password123", "123 Main St", "Italian", "Vegetarian")
    recommendation_system.addUser("Ramesh","pass456","123 Elm St","Chinese","Vegan")
# Add cuisines
    recommendation_system.add_cuisine("Italian")
    recommendation_system.add_cuisine("Chinese")
    recommendation_system.add_cuisine("Mexican")
    recommendation_system.add_cuisine("Indian")
    recommendation_system.add_cuisine("American")
    recommendation_system.add_cuisine("Middle Eastern")

# Add food items
    recommendation_system.addFood("Margherita Pizza", "Italian", 300, 15, 12, 30, ["Vitamin A", "Calcium"], ["Iron"], "Vegetarian", ["Gluten"], "late-night", "Cheesy")
    recommendation_system.addFood("Pasta Primavera", "Italian", 280, 10, 8, 35, ["Vitamin C"], ["Magnesium"], "Vegan", ["Gluten"], "snack", "Herbal")
    recommendation_system.addFood("Kung Pao Chicken", "Chinese", 350, 20, 15, 25, ["Vitamin D"], ["Potassium"], "Nut-Free", ["Soy"], "dinner", "Spicy")
    recommendation_system.addFood("Sweet and Sour Tofu", "Chinese", 250, 15, 10, 30, ["Vitamin B"], ["Iron"], "Vegan", ["Soy"], "lunch", "Sweet and Tangy")
    recommendation_system.addFood("Tacos", "Mexican", 200, 12, 10, 25, ["Vitamin C"], ["Phosphorus"], "Dairy-Free", ["Corn"], "snack", "Savory")
    recommendation_system.addFood("Paneer Butter Masala", "Indian", 400, 18, 20, 35, ["Vitamin E"], ["Calcium"], "Vegetarian", ["Dairy"], "dinner", "Spicy")
    recommendation_system.addFood("Vegan Burrito", "Mexican", 350, 12, 10, 40, ["Vitamin B12"], ["Iron"], "Vegan", [], "lunch", "Earthy and Spicy")
    recommendation_system.addFood("Caesar Salad", "American", 180, 8, 12, 15, ["Vitamin K"], ["Calcium"], "Gluten-Free", ["Dairy"], "snack", "Savory and Fresh")
    recommendation_system.addFood("Gluten-Free Pancakes", "American", 250, 6, 8, 30, ["Vitamin B2"], ["Iron"], "Gluten-Free", ["Dairy"], "breakfast", "Sweet")
    recommendation_system.addFood("Falafel Wrap", "Middle Eastern", 280, 10, 12, 32, ["Vitamin A"], ["Magnesium"], "Vegetarian", ["Gluten"], "lunch", "Herbal and Savory")

# Special offers for some items
    recommendation_system.add_offers("Kung Pao Chicken", "Buy one get one free")
    recommendation_system.add_offers("Tacos", "Free Sweet and sour tofu with order")

#seasonal items
    spring_greens = Ingredient("Spring Mix", [Season.SPRING], 5, 2.50, True)
    pumpkin = Ingredient("Pumpkin", [Season.FALL], 30, 1.75)
    strawberries = Ingredient("Strawberries", [Season.SPRING, Season.SUMMER], 7, 3.00, True)
    chocolate = Ingredient("Dark Chocolate", [], 90, 4.00)
    
    spring_salad = MenuItem("Spring Salad","Fresh greens with seasonal vegetables",12.99,[spring_greens, strawberries],seasons=[Season.SPRING])
    pumpkin_spice = MenuItem("Pumpkin Spice Latte","Warm spiced coffee drink",4.99,[pumpkin],seasons=[Season.FALL])
    valentine_cake = MenuItem("Valentine's Day Special Cake","Heart-shaped chocolate cake",24.99,[chocolate, strawberries],holidays=[Holiday.VALENTINE])
    
    seasonal_menu.add_item(spring_salad)
    seasonal_menu.add_item(pumpkin_spice)
    seasonal_menu.add_item(valentine_cake)
    
    seasonal_menu.record_sale("Spring Salad", 10)
    seasonal_menu.record_sale("Pumpkin Spice Latte", 15)
    
    # Simulate user login
    recommendation_system.login_user()

    while True:
        print("\n--- Food Recommendation System Menu ---")
        print("1. Rate a Dish")
        print("2. Order Food")
        print("3. Print seasonal menu items")
        print("4. Cuisine-Based Recommendations")
        print("5. Show New Arrivals")
        print("6. Personalized Recommendations")
        print("7. Recommend Based on Nutrition")
        print("8. Popular Dishes Recommendations")
        print("9. Time-Based Suggestions")
        print("10. Pair Recommendations")
        print("11. Check Specific Food in Nutrition Tree")
        print("12. Show Special Offers")
        print("0. Exit")

        choice = input("Please select an option (0-12): ")

        if choice == '1':
            cuisine = input("Enter cuisine type: ")
            dish = input("Enter dish name: ")
            rating = int(input("Enter your rating (1-5): "))
            recommendation_system.rate_dish(cuisine, dish, rating)

        elif choice == '2':
            dish = input("Enter the name of the food to order: ")
            quantity = int(input("Enter the quantity: "))
            recommendation_system.order_food(dish, quantity)

        elif choice == '3':
            print("Getting seasonal items")
            seasonal_items = seasonal_menu.get_seasonal_items()
    
            print("\nCurrent Seasonal Menu Items:")
            print("-" * 50)
            for item in seasonal_items:
                print(f"{item['name']}")
                print(f"Description: {item['description']}")
                print(f"Price: ${item['price']:.2f}")
                print(f"Availability: {item['availability']:.2%}")
                print(f"Popularity: {item['popularity']:.2%}")
                print("-" * 50)

        elif choice == '4':
            cuisine = input("Enter cuisine type for recommendations: ")
            recommendation_system.cuisine_based_recommendations(cuisine)

        elif choice == '5':
            print("New arrivals: ")
            recommendation_system.get_new_arrivals()

        elif choice == '6':
            print("Personalized Recommendations:")
            recommendation_system.personalized_recommendations()

        elif choice == '7':
            #print("Recommendations Based on Nutrition:")
            recommendation_system.recommend_based_on_nutrition()

        elif choice == '8':
            print("Popular Dishes Recommendations:")
            recommendation_system.popular_dishes_recommendation()

        elif choice == '9':
            print("Time-Based Suggestions:")
            recommendation_system.time_based_suggestions()

        elif choice == '10':
            dish = input("Enter the name of the dish for pair recommendations: ")
            recommendation_system.pair_recommendations(dish)

        elif choice == '11':
            nutrition_score = int(input("Enter the nutrition score to check: "))
            food = recommendation_system.nutritionTree.get_food(nutrition_score)
            print(f"Food item with nutrition score {nutrition_score}: {food}")

        elif choice == '12':
            recommendation_system.offer_recommendation()

        elif choice == '0':
            print("Exiting the recommendation system. Goodbye!")
            break

        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    main()
