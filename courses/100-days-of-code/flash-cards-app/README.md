# Description
Flash Cards app using tkinter.

# Features
List of features for the app.

1. Flash cards creation

> The front of the flash card consists of an image and/or text, while the back must have at least one of the following: a title, an image, a description text, or a summary text. The summary text can be rewritten after a revision, following the simplify step of the Feynman technique.

2. Projects creation

> A project is like a theme/subject to group flash cards. For example, if a user wants to use flash cards to study English, they can create a project exclusively for this purpose. Users can create and switch between different projects at will.

3. Flash cards priority ranking

> Each project will rank its flash cards according to their priority in descending order. Cards with higher priority will be the ones picked next for revision. Each card will have a priority score that is calculated using the metadata stored in the card.

4. Custom priority ranking

> The user can set a custom function to calculate the priority scores.

5. Flash cards list

> A scrollable list displaying all the flash cards in the current project in descending order of priority. This enables the user to navigate between flash cards freely without relying on the "next card" functionality.

6. Flash cards filter

> Find specific cards based on criteria such as creation date or priority.

7. Quiz mode

> Review cards in a randomized order.

8. _Dark mode_

> Switch dark mode on/off.

9. _Progress tracking_

> Display user progress, like number of reviewd cards, performance over time, and others.

# Planning
The app will implement something similar to the MVC architecture. After the implementation, further readings about the MVC architectural pattern will be done. I may come back to the project later to point out errors in the implementation, suggest improvements, and identify aspects that deviate from the general MVC pattern.

## Data model
The app data will be handled as the following:
- `Card` class, which instances will store the cards data;
- The `Card` class will implement basically getters and setters;
- `Project` class, which instances will store the project data and associated `Card` instances;
- The priority score calculation, cards filtering, and revision mode (priority or quiz mode) will be implemented inside the `Project` class;
- `Project` instances will have methods to return its progress metrics;
- Each `Project` instance will be associated with a individual `<ProjectName>.json` file and will implement methods to update/save the data locally;

## View
The app layout is sketched in [layout.png](./layout.png). Each color represents a group of widgets that will be somewhat independent of each other but related. Each group will implement its own update functionality and generate virtual events related to changes in the widgets within. All groups will be packed inside a `Screen` class and organized within the main window. Since there is still little experience with the tool, not much planning will be done; it will be implemented in a more experimental way.

## Controller
Similarly to the View, little planning will be done for the Controller, and the problem will be approached in an experimental way. The Controller will essentially manage how to handle the generated events, calling the update methods within the `Screen` class.

# Notes
1. I was quite inefficient coding this app;
2. There's just one thread, so the app can freeze when a large computation takes place. However, the more complex calculations are just O(n), with n being the number of flash cards in a single project;
3. Filtering, dark mode, and custom priority functionalities weren't implemented;
4. There's no OOP for the [controller](./main.py), just pure functional programming;
5. I think that Tkinter syntax makes code a bit messy, but I believe the [/views](./views/) can be made more readable;
6. I'm probably skipping some useful checks in the controller and in the views to make sure the user can't break the app;
7. The [model](./model.py) is way better organized that the rest. But I think that the rest in more readable without annotations;
8. `Screen` is now `App`.
