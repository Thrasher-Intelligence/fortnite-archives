#!/usr/bin/env python3

import os
import json
import argparse

def list_versions(base_dir):
    """Lists all available map versions by walking the directory tree."""
    versions = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json") and file == os.path.basename(root):
                relative_path = os.path.relpath(os.path.join(root, file), base_dir)
                version_path = os.path.dirname(relative_path)
                versions.append(version_path)
    return versions

def view_locations(base_dir, version_path):
    """Views all locations in a given version's JSON."""
    file_path = os.path.join(base_dir, version_path, f"{version_path}.json")
    if not os.path.exists(file_path):
        print(f"Error: JSON file not found for version '{version_path}'")
        return

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if "locations" in data and isinstance(data["locations"], list):
                print(f"Locations for version '{version_path}':")
                for location in data["locations"]:
                    print(f"- {location}")
            else:
                print(f"No 'locations' key found or it's not a list in '{file_path}'")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file_path}'")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def add_category(base_dir, category_key, category_value):
    """Adds a new category to every JSON file."""
    updated_count = 0
    error_count = 0
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json") and file == os.path.basename(root):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)

                    if category_key not in data:
                        data[category_key] = category_value
                        with open(file_path, 'w') as f:
                            json.dump(data, f, indent=2)
                        print(f"Added '{category_key}' to '{file_path}'")
                        updated_count += 1
                    else:
                        print(f"Warning: '{category_key}' already exists in '{file_path}'. Skipping.")

                except json.JSONDecodeError:
                    print(f"Error: Could not decode JSON from '{file_path}'. Skipping.")
                    error_count += 1
                except Exception as e:
                    print(f"An unexpected error occurred processing '{file_path}': {e}")
                    error_count += 1

    print(f"\nFinished adding category '{category_key}'. Updated {updated_count} files. Encountered {error_count} errors.")

def main():
    parser = argparse.ArgumentParser(description="Manage Fortnite map versions.")
    parser.add_argument("base_dir", help="The base directory containing map versions.")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    parser_list = subparsers.add_parser("list", help="List all available map versions.")

    # View command
    parser_view = subparsers.add_parser("view", help="View locations for a specific version.")
    parser_view.add_argument("version_path", help="The path to the version directory (e.g., chapter_1/season_1/1.6.0).")

    # Add category command
    parser_add = subparsers.add_parser("add-category", help="Add a new category to all JSON files.")
    parser_add.add_argument("category_key", help="The category key to add (e.g., 'notes').")
    parser_add.add_argument("category_value", help="The default value for the new category (e.g., '').")

    args = parser.parse_args()

    if not os.path.isdir(args.base_dir):
        print(f"Error: Base directory '{args.base_dir}' not found.")
        return

    if args.command == "list":
        versions = list_versions(args.base_dir)
        if versions:
            print("Available map versions:")
            for version in versions:
                print(f"- {version}")
        else:
            print("No map versions found.")
    elif args.command == "view":
        view_locations(args.base_dir, args.version_path)
    elif args.command == "add-category":
        add_category(args.base_dir, args.category_key, args.category_value)
    else:
        parser.print_help()

if __name__ == "__main__":
    # Sample Usage:
    #
    # List all versions in a directory named 'map_data':
    # python mapmanager.py map_data list
    #
    # View locations for version 'chapter_1/season_1/1.6.0':
    # python mapmanager.py map_data view chapter_1/season_1/1.6.0
    #
    # Add a 'notes' category with an empty string value to all JSON files:
    # python mapmanager.py map_data add-category notes ""

    main()
