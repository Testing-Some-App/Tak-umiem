# Overview

This is a simple Polish desktop application for rolling two 4-sided dice, built using Python's tkinter GUI framework. The application provides a graphical interface for dice rolling functionality with Polish language localization.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **GUI Framework**: tkinter with ttk for modern widget styling
- **Application Structure**: Single-class architecture (`DiceRollerApp`) following object-oriented design principles
- **Window Management**: Fixed-size window (400x300) with automatic screen centering
- **Localization**: Polish language interface and comments

## Core Components
- **Main Application Class**: `DiceRollerApp` handles all GUI logic and dice rolling functionality
- **State Management**: Simple instance variables to track dice values and sum
- **Event Handling**: Button-based interaction for dice rolling operations
- **Random Number Generation**: Python's built-in `random` module for dice roll simulation

## Design Patterns
- **Single Responsibility**: Each method handles a specific aspect (window centering, widget creation, etc.)
- **Encapsulation**: All application logic contained within the main class
- **Separation of Concerns**: UI creation separated from business logic

# External Dependencies

## Standard Library Dependencies
- **tkinter**: Core GUI framework for desktop application
- **random**: Dice roll randomization functionality

## Runtime Requirements
- **Python 3**: Application requires Python 3 interpreter
- **Platform**: Cross-platform desktop application (Windows, macOS, Linux)

Note: This is a standalone desktop application with no external service integrations, databases, or network dependencies.