#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_USERS 100

// User structure to store user information
typedef struct {
    char name[20];
    int finalScore;
} User;

User users[MAX_USERS]; // Array to store multiple users
int userCount = 0; // Counter to keep track of the number of users

// Function prototypes
void menu();
void addUserScore(char *name, int score);
void displayLeaderboard();
void startGame();
int beginnerCQuiz();
int intermediateCQuiz();
int advancedCQuiz();

int main() {
    int choice;

    do {
        // Display menu
        menu();
        printf("\nEnter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                // Start the quiz game
                startGame();
                break;
            case 2:
                // Display leaderboard
                displayLeaderboard();
                break;
            case 3:
                // Exit the program
                printf("\nExiting the program. Thank you!\n");
                exit(0);
            default:
                printf("\nInvalid choice! Please try again.\n");
        }
    } while (1);

    return 0;
}

void menu() {
    printf("\n=============================");
    printf("\n WELCOME TO THE C QUIZ GAME ");
    printf("\n=============================");
    printf("\n1. Start Game");
    printf("\n2. View Leaderboard");
    printf("\n3. Exit");
    printf("\n=============================\n");
}

// Function to add user score to the leaderboard
void addUserScore(char *name, int score) {
    if (userCount < MAX_USERS) {
        strcpy(users[userCount].name, name);
        users[userCount].finalScore = score;
        userCount++;
    } else {
        printf("Leaderboard is full!\n");
    }
}

// Function to display the leaderboard
void displayLeaderboard() {
    // Sort the leaderboard based on scores in descending order
    for (int i = 0; i < userCount - 1; i++) {
        for (int j = i + 1; j < userCount; j++) {
            if (users[i].finalScore < users[j].finalScore) {
                User temp = users[i];
                users[i] = users[j];
                users[j] = temp;
            }
        }
    }

    printf("\n=============================");
    printf("\n         LEADERBOARD         ");
    printf("\n=============================");
    printf("\nRank\tName\t\tScore\n");
    for (int i = 0; i < userCount; i++) {
        printf("%d\t%s\t\t%d\n", i + 1, users[i].name, users[i].finalScore);
    }
}

// Function to start the game
void startGame() {
    char name[20];
    int CFinalScore = 0;

    // Get the user's name
    printf("\nEnter your First Name: ");
    scanf("%s", name);

    printf("\nStarting the quiz...\n");

    // Start all quiz levels
    CFinalScore += beginnerCQuiz();
    CFinalScore += intermediateCQuiz();
    CFinalScore += advancedCQuiz();

    // Add the score to the leaderboard
    addUserScore(name, CFinalScore);

    printf("\nYour total score is: %d\n", CFinalScore);
    printf("\nReturning to the main menu...\n");
}

// Beginner Quiz
int beginnerCQuiz() {
    const char *questions[] = {
        "1. Which symbol is used to end a statement in C?",
        "2. Which data type is used to store whole numbers in C?",
        "3. How do you start a comment in C?",
        "4. What does 'int' stand for in C?",
        "5. Which function is used to output text to the console?"
    };

    const char *options[][4] = {
        {"A. :", "B. ;", "C. .", "D. ,"},
        {"A. char", "B. int", "C. float", "D. double"},
        {"A. //", "B. /**/", "C. #", "D. !!"},
        {"A. integer", "B. integration", "C. intent", "D. internal"},
        {"A. printf()", "B. cout", "C. print()", "D. echo"}
    };

    const char answers[] = {'B', 'B', 'A', 'A', 'A'};
    int score = 0;
    char answer;

    printf("\n=============================");
    printf("\n BEGINNER LEVEL C QUIZ ");
    printf("\n=============================");

    for (int i = 0; i < 5; i++) {
        printf("\n%s\n", questions[i]);
        printf("%s\n%s\n%s\n%s\n", options[i][0], options[i][1], options[i][2], options[i][3]);
        printf("Enter your answer: ");
        scanf(" %c", &answer);

        if (answer == answers[i] || answer == (answers[i] + 32)) {
            printf("Correct!\n");
            score++;
        } else {
            printf("Wrong! Correct answer is %c\n", answers[i]);
        }
    }

    printf("Your score in Beginner Level is: %d out of 5\n", score);
    return score;
}

// Intermediate Quiz
int intermediateCQuiz() {
    const char *questions[] = {
        "1. What does '&&' represent in C?",
        "2. Which operator is used for modulo operation?",
        "3. How would you declare an array of integers?",
        "4. How do you allocate memory dynamically in C?",
        "5. Which header file is required for string functions?"
    };

    const char *options[][4] = {
        {"A. OR", "B. AND", "C. NOT", "D. XOR"},
        {"A. #", "B. %%", "C. %%", "D. %"},
        {"A. int array[]", "B. int array(5)", "C. int array{}", "D. int array<>"},
        {"A. malloc()", "B. memalloc()", "C. alloc()", "D. calloc()"},
        {"A. stdio.h", "B. stdlib.h", "C. string.h", "D. strings.h"}
    };

    const char answers[] = {'B', 'D', 'A', 'A', 'C'};
    int score = 0;
    char answer;

    printf("\n=============================");
    printf("\n INTERMEDIATE LEVEL C QUIZ ");
    printf("\n=============================");

    for (int i = 0; i < 5; i++) {
        printf("\n%s\n", questions[i]);
        printf("%s\n%s\n%s\n%s\n", options[i][0], options[i][1], options[i][2], options[i][3]);
        printf("Enter your answer: ");
        scanf(" %c", &answer);

        if (answer == answers[i] || answer == (answers[i] + 32)) {
            printf("Correct!\n");
            score++;
        } else {
            printf("Wrong! Correct answer is %c\n", answers[i]);
        }
    }

    printf("Your score in Intermediate Level is: %d out of 5\n", score);
    return score;
}

// Advanced Quiz
int advancedCQuiz() {
    const char *questions[] = {
        "1. Which function deallocates memory in C?",
        "2. What is the output type of the sizeof operator?",
        "3. Which of the following is a pointer declaration?",
        "4. Which keyword is used to prevent modifying a variable?",
        "5. Which function is used to copy a string?"
    };

    const char *options[][4] = {
        {"A. free()", "B. malloc()", "C. remove()", "D. dealloc()"},
        {"A. int", "B. long", "C. float", "D. size_t"},
        {"A. int ptr", "B. int ptr()", "C. int *ptr", "D. ptr int*"},
        {"A. constant", "B. immutable", "C. const", "D. static"},
        {"A. strcpy()", "B. memcpy()", "C. strcat()", "D. copy()"}
    };

    const char answers[] = {'A', 'D', 'C', 'C', 'A'};
    int score = 0;
    char answer;

    printf("\n=============================");
    printf("\n ADVANCED LEVEL C QUIZ ");
    printf("\n=============================");

    for (int i = 0; i < 5; i++) {
        printf("\n%s\n", questions[i]);
        printf("%s\n%s\n%s\n%s\n", options[i][0], options[i][1], options[i][2], options[i][3]);
        printf("Enter your answer: ");
        scanf(" %c", &answer);

        if (answer == answers[i] || answer == (answers[i] + 32)) {
            printf("Correct!\n");
            score++;
        } else {
            printf("Wrong! Correct answer is %c\n", answers[i]);
        }
    }

    printf("Your score in Advanced Level is: %d out of 5\n", score);
    return score;
}
