"""
Generates arbitrary daycares
"""
import random
from base.DatabaseDriver import *
from tables.ChildInstance import ChildInstance
from tables.ChildInstanceDBEntry import ChildInstanceDBEntry
from tables.ClassroomInstance import ClassroomInstance
from tables.ClassroomInstanceDBEntry import ClassroomInstanceDBEntry
from tables.FacilityInstance import FacilityInstance
from tables.FacilityInstanceDBEntry import FacilityInstanceDBEntry
from tables.TeacherInstance import TeacherInstance
from tables.TeacherInstanceDBEntry import TeacherInstanceDBEntry

facilityNames = [
    "Sunshine",
    "Rainbow",
    "Tiny",
    "Little",
    "Happy",
    "Smiles",
    "Playful",
    "Bright",
    "Cheerful",
    "Giggles",
    "Cuddles",
    "Dreamy",
    "Joyful",
    "Magic",
    "Star",
    "Cherubs",
    "Meadow",
    "Blossom",
    "Tender",
    "Nurturing",
    "Harmony",
    "Lullaby",
    "Adventure",
    "Discovery",
    "Wonder",
    "Buddy",
    "Kiddie",
    "Tots",
    "Tiny Tots",
    "Dreamland",
    "Sweet Pea",
    "Pumpkin",
    "Little Lamb",
    "Angel",
    "Honey Bee",
    "Candyland",
    "Teddy Bear",
    "Snuggle",
    "Sugar Plum"
]

classroomNames = [
    "Math Mania",
    "Science Explorers",
    "Art Adventures",
    "Music Makers",
    "Literacy Land",
    "Nature Discovery",
    "Outdoor Explorations",
    "Sensory Play",
    "Language Learners",
    "Dramatic Play",
    "Social Studies Safari",
    "Health and Wellness",
    "Physical Education",
    "Cultural Connections",
    "Community Helpers",
    "Technology Time",
    "Gardening Guru",
    "Cooking Creations",
    "Storytelling Circle",
    "Puzzle Paradise",
    "Creative Crafts",
    "Animal Antics",
    "Building Blocks",
    "Water World",
    "Mindful Moments",
    "Dance Dynamics",
    "Imagination Station",
    "Inquiry Investigations",
    "Friendship Fun",
    "Expressive Arts",
    "Super Science",
    "Exploration Express",
    "Wonderful World of Words",
    "Adventure Alley",
    "Healthy Habits",
    "STEAM Studio",
    "Math Magic",
    "Discovery Depot",
    "Exploring Emotions",
    "Amazing Authors"
]

firstNames = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Isabella", "James", "Sophia", "Logan",
    "Charlotte", "Benjamin", "Amelia", "Mason", "Evelyn", "Elijah", "Abigail", "Oliver", "Harper",
    "Jacob", "Emily", "Michael", "Elizabeth", "Alexander", "Mia", "Ethan", "Ella", "Daniel", "Avery",
    "Henry", "Sofia", "Jackson", "Camila", "Sebastian", "Aria", "Aiden", "Scarlett", "Matthew", "Madison",
    "Samuel", "Luna", "David", "Grace"
]

lastNames = [
    "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
    "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
    "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright",
    "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter", "Mitchell", "Perez"
]


class DaycareGenerator:

    def __init__(self, database):
        self.database = database

    def _generateFacilityEntry(self) -> FacilityInstanceDBEntry:
        facilityName = random.choice(facilityNames)
        facility = FacilityInstance(
            name = facilityName,
        )
        return FacilityInstanceDBEntry(facility)

    def _generateClassroomEntry(self, facility: FacilityInstanceDBEntry) -> ClassroomInstanceDBEntry:
        classroomName = random.choice(classroomNames)
        classroom = ClassroomInstance(
            name = classroomName,
            capacity = random.randint(1, 40),
            facility = facility
        )
        return ClassroomInstanceDBEntry(classroom)

    def _generateTeacherEntry(self, classroom: ClassroomInstanceDBEntry) -> TeacherInstanceDBEntry:
        teacherFirstName = random.choice(firstNames)
        teacherLastName = random.choice(lastNames)
        teacher = TeacherInstance(
            firstname = teacherFirstName,
            lastname = teacherLastName,
            room = classroom
        )
        return TeacherInstanceDBEntry(teacher)

    def _generateChildEntry(self, classroom: ClassroomInstanceDBEntry) -> ChildInstanceDBEntry:
        childFirstName = random.choice(firstNames)
        childLastName = random.choice(lastNames)
        childAge = random.randint(1, 10)
        child = ChildInstance(
            firstname = childFirstName,
            lastname = childLastName,
            age = childAge,
            room = classroom
        )
        return ChildInstanceDBEntry(child)

    def generateDaycares(self, facilityAmt: int, classroomAmtRange: tuple):
        generatedDaycares = []
        # Generate our daycares
        for _ in range(facilityAmt):
            facility = self._generateFacilityEntry()
            self.database.generateEntry(facility)

            # In our daycares, generate classrooms
            for _ in range(random.randint(*classroomAmtRange)):
                classroom = self._generateClassroomEntry(facility)
                self.database.generateEntry(classroom)
                facility.classrooms.append(classroom)
                facility.classroomid = classroom.id
                childEntries = []
                teacherEntries = []

                # Depending on how many kids can be in the room, randrange
                for _ in range(random.randint(1, classroom.capacity)):
                    child = self._generateChildEntry(classroom)
                    self.database.generateEntry(child)
                    classroom.children.append(child)
                    childEntries.append(child)

                # Subgroups children into lists with at most 10 kids in one
                # Len of childGroups = number of teachers we need
                childGroups = [childEntries[i:i + 10] for i in range(0, len(childEntries), 10)]
                for neededTeachers in range(len(childGroups)):
                    teacher = self._generateTeacherEntry(classroom)
                    self.database.generateEntry(teacher)

                    # classroom.teacherids.append(teacher.id)
                    classroom.teacherids = teacher.id

                    classroom.teachers.append(teacher)
                    teacherEntries.append(teacher)
                    # Register each child w teacher
                    for child in childGroups[neededTeachers]:
                        teacher.children.append(child)
                        teacher.childids = child.id

            generatedDaycares.append(facility)
        return generatedDaycares


if __name__ == "__main__":
    """
    Driver code; when ran, will insert arbitrary day care entries into the database.
    """
    # Generate our DB
    # database = DatabaseManager(Config)
    # database.initSession()

    facilityAmt = 2
    for genDaycare in DaycareGenerator(Database).generateDaycares(facilityAmt, (1, 10)):
        Database.generateEntry(genDaycare)
    print(f"Generated {facilityAmt} daycares!")
