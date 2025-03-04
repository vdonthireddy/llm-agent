from neo4j import GraphDatabase
from typing import Any

class KnowledgeGraph:
    def __init__(self, uri: str, username: str, password: str):
        """Initialize the Neo4j connection."""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        """Close the Neo4j connection."""
        self.driver.close()

    def create_person(self, name: str, age: int) -> None:
        """Create a Person node."""
        with self.driver.session() as session:
            session.execute_write(self._create_person, name, age)

    @staticmethod
    def _create_person(tx, name: str, age: int) -> None:
        query = """
        CREATE (p:Person {name: $name, age: $age})
        RETURN p
        """
        tx.run(query, name=name, age=age)

    def create_friendship(self, person1_name: str, person2_name: str) -> None:
        """Create a FRIENDS_WITH relationship between two persons."""
        with self.driver.session() as session:
            session.execute_write(self._create_friendship, person1_name, person2_name)

    @staticmethod
    def _create_friendship(tx, person1_name: str, person2_name: str) -> None:
        query = """
        MATCH (p1:Person {name: $person1_name})
        MATCH (p2:Person {name: $person2_name})
        CREATE (p1)-[:FRIENDS_WITH]->(p2)
        """
        tx.run(query, person1_name=person1_name, person2_name=person2_name)

    def find_friends_of_friends(self, person_name: str) -> list:
        """Find friends of friends for a given person."""
        with self.driver.session() as session:
            result = session.execute_read(self._find_friends_of_friends, person_name)
            return result

    @staticmethod
    def _find_friends_of_friends(tx, person_name: str) -> list:
        query = """
        MATCH (p:Person {name: $person_name})-[:FRIENDS_WITH]->(friend)-[:FRIENDS_WITH]->(friend_of_friend)
        WHERE p <> friend_of_friend
        RETURN DISTINCT friend_of_friend.name as name
        """
        result = tx.run(query, person_name=person_name)
        return [record["name"] for record in result]

def main():
    # Replace with your Neo4j connection details
    uri = "neo4j://localhost:7687"
    username = "neo4j"
    password = "VjD0nP@s3w0rd"

    # Create a knowledge graph instance
    kg = KnowledgeGraph(uri, username, password)

    try:
        # Create some person nodes
        kg.create_person("Alice", 30)
        kg.create_person("Bob", 31)
        kg.create_person("Charlie", 32)
        kg.create_person("David", 33)

        # Create friendship relationships
        kg.create_friendship("Alice", "Bob")
        kg.create_friendship("Bob", "Charlie")
        kg.create_friendship("Charlie", "David")

        # Find friends of friends for Alice
        friends_of_friends = kg.find_friends_of_friends("Alice")
        print(f"Alice's friends of friends: {friends_of_friends}")

    finally:
        kg.close()

if __name__ == "__main__":
    main()