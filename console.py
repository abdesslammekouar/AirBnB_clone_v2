#!/usr/bin/python3
"""Console Module"""
import cmd
import sys
import re
import os
from datetime import datetime
import uuid
from models.base_model import BaseModel
from models import storage
from models.user import User
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.review import Review


class HBNBCommand(cmd.Cmd):
    """Contains the functionality for the HBNB console"""

    # Determines the prompt for interactive/non-interactive modes
    prompt = '(hbnb) ' if sys.__stdin__.isatty() else ''

    classes = {
        'BaseModel': BaseModel, 'User': User, 'Place': Place,
        'State': State, 'City': City, 'Amenity': Amenity,
        'Review': Review
    }
    dot_cmds = ['all', 'count', 'show', 'destroy', 'update']
    types = {
        'number_rooms': int, 'number_bathrooms': int,
        'max_guest': int, 'price_by_night': int,
        'latitude': float, 'longitude': float
    }

    def preloop(self):
        """Prints if isatty is false"""
        if not sys.__stdin__.isatty():
            print('(hbnb)')

    def precmd(self, line):
        """Reformat command line for advanced command syntax."""
        _cmd = _cls = _id = _args = ''  # Initialize line elements

        # Scan for general formatting - i.e., '.', '(', ')'
        if not ('.' in line and '(' in line and ')' in line):
            return line

        try:  # Parse line left to right
            pline = line[:]  # Parsed line

            # Isolate <class name>
            _cls = pline[:pline.find('.')]

            # Isolate and validate <command>
            _cmd = pline[pline.find('.') + 1:pline.find('(')]
            if _cmd not in HBNBCommand.dot_cmds:
                raise Exception

            # If parentheses contain arguments, parse them
            pline = pline[pline.find('(') + 1:pline.find(')')]
            if pline:
                # Partition args: (<id>, [<delim>], [<*args>])
                pline = pline.partition(', ')  # pline converted to a tuple

                # Isolate _id, stripping quotes
                _id = pline[0].replace('\"', '')

                # If arguments exist beyond _id
                pline = pline[2].strip()  # pline is now a str
                if pline:
                    # Check for *args or **kwargs
                    if (pline[0] == '{' and pline[-1] == '}' and
                            isinstance(eval(pline), dict)):
                        _args = pline
                    else:
                        _args = pline.replace(',', '')
            line = ' '.join([_cmd, _cls, _id, _args])

        except Exception as mess:
            pass
        finally:
            return line

    def postcmd(self, stop, line):
        """Prints if isatty is false"""
        if not sys.__stdin__.isatty():
            print('(hbnb) ', end='')
        return stop

    def do_quit(self, command):
        """Method to exit the HBNB console"""
        exit(0)

    def help_quit(self):
        """Prints the help documentation for quit"""
        print("Exits the program with formatting\n")

    def do_EOF(self, arg):
        """Handles EOF to exit the program"""
        print()
        exit(0)

    def help_EOF(self):
        """Prints the help documentation for EOF"""
        print("Exits the program without formatting\n")

    def emptyline(self):
        """Overrides the emptyline method of CMD"""
        pass

    def do_create(self, args):
        """Create an object of any class"""
        ignored_attrs = ('id', 'created_at', 'updated_at', '__class__')
        class_name = ''
        name_pattern = r'(?P<name>(?:[a-zA-Z]|_)(?:[a-zA-Z]|\d|_)*)'
        class_match = re.match(name_pattern, args)
        obj_kwargs = {}
        if class_match is not None:
            class_name = class_match.group('name')
            params_str = args[len(class_name):].strip()
            params = params_str.split(' ')
            str_pattern = r'(?P<t_str>"([^"]|\")*")'
            float_pattern = r'(?P<t_float>[-+]?\d+\.\d+)'
            int_pattern = r'(?P<t_int>[-+]?\d+)'
            param_pattern = '{}=({}|{}|{})'.format(
                name_pattern,
                str_pattern,
                float_pattern,
                int_pattern
            )
            for param in params:
                param_match = re.fullmatch(param_pattern, param)
                if param_match is not None:
                    key_name = param_match.group('name')
                    str_v = param_match.group('t_str')
                    float_v = param_match.group('t_float')
                    int_v = param_match.group('t_int')
                    if float_v is not None:
                        obj_kwargs[key_name] = float(float_v)
                    if int_v is not None:
                        obj_kwargs[key_name] = int(int_v)
                    if str_v is not None:
                        obj_kwargs[key_name] = str_v[1:-1].replace('_', ' ')
        else:
            class_name = args
        if not class_name:
            print("** class name missing **")
            return
        elif class_name not in HBNBCommand.classes:
            print("** class doesn't exist **")
            return
        if os.getenv('HBNB_TYPE_STORAGE') == 'db':
            if 'id' not in obj_kwargs:
                obj_kwargs['id'] = str(uuid.uuid4())
            if 'created_at' not in obj_kwargs:
                obj_kwargs['created_at'] = str(datetime.now())
            if 'updated_at' not in obj_kwargs:
                obj_kwargs['updated_at'] = str(datetime.now())
            new_instance = HBNBCommand.classes[class_name](**obj_kwargs)
            new_instance.save()
            print(new_instance.id)
        else:
            new_instance = HBNBCommand.classes[class_name]()
            for key, value in obj_kwargs.items():
                if key not in ignored_attrs:
                    setattr(new_instance, key, value)
            new_instance.save()
            print(new_instance.id)

    def help_create(self):
        """Help information for the create method"""
        print("Creates an object of any class")
        print("[Usage]: create <className>\n")

    def do_show(self, args):
        """Method to show an individual object"""
        new = args.partition(" ")
        class_name = new[0]
        object_id = new[2]

        # Guard against trailing args
        if object_id and ' ' in object_id:
            object_id = object_id.partition(' ')[0]

        if not class_name:
            print("** class name missing **")
            return

        if class_name not in HBNBCommand.classes:
            print("** class doesn't exist **")
            return

        if not object_id:
            print("** instance id missing **")
            return

        key = class_name + "." + object_id
        try:
            print(storage.all()[key])
        except KeyError:
            print("** no instance found **")

    def help_show(self):
        """Help information for the show command"""
        print("Shows an individual instance of a class")
        print("[Usage]: show <className> <objectId>\n")

    def do_destroy(self, args):
        """Destroys a specified object"""
        new = args.partition(" ")
        class_name = new[0]
        object_id = new[2]
        if object_id and ' ' in object_id:
            object_id = object_id.partition(' ')[0]

        if not class_name:
            print("** class name missing **")
            return

        if class_name not in HBNBCommand.classes:
            print("** class doesn't exist **")
            return

        if not object_id:
            print("** instance id missing **")
            return

        key = class_name + "." + object_id

        try:
            storage.delete(storage.all()[key])
            storage.save()
        except KeyError:
            print("** no instance found **")

    def help_destroy(self):
        """Help information for the destroy command"""
        print("Destroys an individual instance of a class")
        print("[Usage]: destroy <className> <objectId>\n")

    def do_all(self, args):
        """Shows all objects, or all objects of a class"""
        print_list = []

        if args:
            args = args.split(' ')[0]  # Remove possible trailing args
            if args not in HBNBCommand.classes:
                print("** class doesn't exist **")
                return
            for k, v in storage.all().items():
                if k.split('.')[0] == args:
                    print_list.append(str(v))
        else:
            for k, v in storage.all().items():
                print_list.append(str(v))

        print(print_list)

    def help_all(self):
        """Help information for the all command"""
        print("Shows all objects, or all of a class")
        print("[Usage]: all <className>\n")

    def do_count(self, args):
        """Count current number of class instances"""
        count = 0
        for k, v in storage.all().items():
            if args == k.split('.')[0]:
                count += 1
        print(count)

    def help_count(self):
        """Help information for the count command"""
        print("Usage: count <class_name>")

    def do_update(self, args):
        """Updates a certain object with new info"""
        class_name = object_id = attribute_name = attribute_value = kwargs = ''

        # Isolate cls from id/args, ex: (<cls>, delim, <id/args>)
        args = args.partition(" ")
        if args[0]:
            class_name = args[0]
        else:  # Class name not present
            print("** class name missing **")
            return
        if class_name not in HBNBCommand.classes:  # Class name invalid
            print("** class doesn't exist **")
            return

        # Isolate id from args
        args = args[2].partition(" ")
        if args[0]:
            object_id = args[0]
        else:  # Id not present
            print("** instance id missing **")
            return

        # Generate key from class and id
        key = class_name + "." + object_id

        # Determine if key is present
        if key not in storage.all():
            print("** no instance found **")
            return

        # First determine if kwargs or args
        if '{' in args[2] and '}' in args[2] and isinstance(eval(args[2]), dict):
            kwargs = eval(args[2])
            args = []  # Reformat kwargs into list, ex: [<name>, <value>, ...]
            for k, v in kwargs.items():
                args.append(k)
                args.append(v)
        else:  # Isolate args
            args = args[2]
            if args and args[0] == '\"':  # Check for quoted arg
                second_quote = args.find('\"', 1)
                attribute_name = args[1:second_quote]
                args = args[second_quote + 1:]

            args = args.partition(' ')

            # If attribute_name was not a quoted arg
            if not attribute_name and args[0] != ' ':
                attribute_name = args[0]
            # Check for quoted value arg
            if args[2] and args[2][0] == '\"':
                attribute_value = args[2][1:args[2].find('\"', 1)]

            # If attribute_value was not a quoted arg
            if not attribute_value and args[2]:
                attribute_value = args[2].partition(' ')[0]

            args = [attribute_name, attribute_value]

        # Retrieve dictionary of current objects
        new_dict = storage.all()[key]

        # Iterate through attribute names and values
        for i, attribute_name in enumerate(args):
            # Block only runs on even iterations
            if (i % 2 == 0):
                attribute_value = args[i + 1]  # Following item is value
                if not attribute_name:  # Check for attribute_name
                    print("** attribute name missing **")
                    return
                if not attribute_value:  # Check for attribute_value
                    print("** value missing **")
                    return
                # Type cast as necessary
                if attribute_name in HBNBCommand.types:
                    attribute_value = HBNBCommand.types[attribute_name](attribute_value)

                # Update dictionary with name, value pair
                new_dict.__dict__.update({attribute_name: attribute_value})

        new_dict.save()  # Save updates to file

    def help_update(self):
        """Help information for the update class"""
        print("Updates an object with new information")
        print("Usage: update <className> <id> <attName> <attVal>\n")


if __name__ == "__main__":
    HBNBCommand().cmdloop()
