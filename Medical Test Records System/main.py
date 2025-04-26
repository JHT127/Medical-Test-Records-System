from _datetime import datetime

class Patient:
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.test_records = []  # start with empty list

    def add_test_record(self, test_name, test_date_time, result_value, unit, status, result_date_time=None):
        test_record = {
            "test_name": test_name,
            "test_date_time": test_date_time,
            "result_value": result_value,
            "unit": unit,
            "status": status,
            "result_date_time": result_date_time
        }
        self.test_records.append(test_record)  # Adds a record to the list

    def get_records_by_date_range(self, start_date, end_date):
        matching_records1 = []
        for record in self.test_records:
            if start_date <= record.test_date_time <= end_date:
                matching_records1.append(record)
                return matching_records1

    def update_test_record(self, test_name, **kwargs):
        for record in self.test_records:
            if record["test_name"] == test_name:
                for key, value in kwargs.items():
                    if key in record:
                        record[key] = value

    def get_records_by_status(self, status):
        matching_records2 = []
        for record in self.test_records:
            if record["status"] == status:
                matching_records2.append(record)
                return matching_records2


###############################################################
class MedicalTestSystem:

    def __init__(self, record_file, test_file):
        self.record_file = record_file
        self.test_file = test_file
        self.patients = {}
        self.tests = {}
        self.valid_statuses = {"Pending", "Completed", "Reviewed"}

    def load_test(self):
        try:
            file = open(self.test_file, 'r')
            try:
                for line in file:
                    name, range_values, unit, turnaround_time = line.strip().split('; ')
                    self.tests[name] = {
                        "range": range_values,
                        "unit": unit,
                        "turnaround_time": turnaround_time
                    }
            finally:
                file.close()
        except FileNotFoundError:
            print(f"File {self.test_file} not found.")

    def load_records(self):
        try:
            file = open(self.record_file, 'r')
            try:
                for line in file:
                    # Split the patient ID from the rest of the details
                    patient_id, test_details = line.strip().split(': ', 1)

                    # Split the test details into individual components
                    details = test_details.split(', ')

                    # Assign the components to variables
                    test_name = details[0]
                    test_date_time = details[1]
                    result_value = details[2]
                    unit = details[3]
                    status = details[4]

                    # Handle optional result_date_time if provided
                    result_date_time = details[5] if len(details) > 5 else None

                    # Check if the patient already exists; if not, add the patient
                    if patient_id not in self.patients:
                        self.patients[patient_id] = Patient(patient_id)

                    # Add the test record to the patient's record
                    self.patients[patient_id].add_test_record(
                        test_name, test_date_time, result_value, unit, status, result_date_time
                    )
            finally:
                file.close()
        except FileNotFoundError:
            print(f"File {self.record_file} not found.")

    def save_records(self):
        file = open(self.record_file, 'w')
        try:
            for patient in self.patients.values():
                for record in patient.test_records:
                    line = (
                        f"{patient.patient_id}: {record['test_name']}, "
                        f"{record['test_date_time']}, {record['result_value']}, "
                        f"{record['unit']}, {record['status']}"
                    )
                    if record['result_date_time']:
                        line += f", {record['result_date_time']}"
                    file.write(line + '\n')
        finally:
            file.close()

    def is_valid_patient_id(self, patient_id):
        return len(patient_id) == 7 and patient_id.isdigit()

    def is_valid_test_name(self, test_name):
        # Assuming a fixed length of 20 characters for test name
        return len(test_name) <= 20

    def is_valid_date_time(self, date_time_str):
        # Check if the input is in the correct format
        if len(date_time_str) != 16 or date_time_str[10] != ' ' or date_time_str[13] != ':':
            print("Invalid Date and Time format. Please use YYYY-MM-DD HH:MM.")
            return False

        # Extract year, month, day, hour, minute from the input
        try:
            year = int(date_time_str[:4])
            month = int(date_time_str[5:7])
            day = int(date_time_str[8:10])
            hour = int(date_time_str[11:13])
            minute = int(date_time_str[14:16])
        except ValueError:
            print("Invalid Date and Time format. Please use YYYY-MM-DD HH:MM.")
            return False

        # Validate year (basic check)
        if year < 1:
            print("Invalid Date and Time. The year must be a positive number.")
            return False

        # Validate month
        if month < 1 or month > 12:
            print("Invalid Date and Time. The month must be between 01 and 12.")
            return False

        # Validate day (taking into account the maximum days in a month)
        days_in_month = [31, 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28, 31, 30, 31, 30,
                         31, 31, 30, 31, 30, 31]
        if day < 1 or day > days_in_month[month - 1]:
            print("Invalid Date and Time. The day must be valid for the given month.")
            return False

        # Validate hour
        if hour < 0 or hour > 23:
            print("Invalid Date and Time. The hour must be between 00 and 23.")
            return False

        # Validate minute
        if minute < 0 or minute > 59:
            print("Invalid Date and Time. The minute must be between 00 and 59.")
            return False

        try:
            # Parse the input date and time to check format and validity
            input_date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")

            # Check if the date is in the future
            if input_date_time > datetime.now():
                print("Invalid Date and Time. The date cannot be in the future.")
                return False

            # If all validations pass, return True
            return True

        except ValueError:
            print("Invalid Date and Time. Please use a valid date in the format YYYY-MM-DD HH:MM.")
            return False

    def is_valid_numeric(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def is_valid_unit(self, unit):
        # Assuming a fixed length of 10 characters for unit
        return len(unit) <= 10

    def is_valid_status(self, status):
        return status in self.valid_statuses

    def add_test_record(self, patient_id, test_name, test_date_time, result_value, unit, status, result_date_time=None):

        if patient_id not in self.patients:
            self.patients[patient_id] = Patient(patient_id)

        self.patients[patient_id].add_test_record(
            test_name, test_date_time, result_value, unit, status, result_date_time
        )
        self.save_records()
        print("Test record added successfully.")

    def update_test_record(self, patient_id, test_name, **kwargs):
        if patient_id not in self.patients:
            print("Patient ID does not exist.")
            return

        # Retrieve the current record
        patient = self.patients[patient_id]
        record_found = False
        for record in patient.test_records:
            if record["test_name"] == test_name:
                record_found = True

                # Update each field with validation
                if 'test_date_time' in kwargs:
                    if self.is_valid_date_time(kwargs['test_date_time']):
                        record['test_date_time'] = kwargs['test_date_time']
                    else:
                        print("Invalid Test Date and Time format.")

                if 'result_value' in kwargs:
                    if self.is_valid_numeric(kwargs['result_value']):
                        record['result_value'] = kwargs['result_value']
                    else:
                        print("Invalid Result Value. It should be a numeric value.")

                if 'unit' in kwargs:
                    if self.is_valid_unit(kwargs['unit']):
                        record['unit'] = kwargs['unit']
                    else:
                        print("Invalid Unit. It should not exceed the maximum length.")

                if 'status' in kwargs:
                    if self.is_valid_status(kwargs['status']):
                        record['status'] = kwargs['status']
                    else:
                        print("Invalid Status. It should be one of 'Pending', 'Completed', 'Reviewed'.")

                if 'result_date_time' in kwargs:
                    if kwargs['result_date_time'] == "" or self.is_valid_date_time(kwargs['result_date_time']):
                        record['result_date_time'] = kwargs['result_date_time'] if kwargs['result_date_time'] else None
                    else:
                        print("Invalid Result Date and Time format.")

                # Save changes after updating
                self.save_records()
                print("Test record updated successfully.")
                break

        if not record_found:
            print("Test record not found.")

    def delete_record(self, patient_id, test_name, test_date_time, result_value, unit, status, result_date_time):
        # Check if the patient ID exists in the patients dictionary
        if patient_id in self.patients:
            # Retrieve the list of test records for the patient
            current_records = self.patients[patient_id].test_records

            # Flag to check if any record was found and deleted
            record_found = False

            # Filter out the record with matching details
            updated_records = []
            for record in current_records:
                if (record['test_name'] == test_name and
                        record['test_date_time'] == test_date_time and
                        record['result_value'] == result_value and
                        record['unit'] == unit and
                        record['status'] == status and
                        (record['result_date_time'] if record['result_date_time'] else '') == result_date_time):
                    record_found = True
                    continue  # Skip this record
                updated_records.append(record)

            # Update the patient's test records with the filtered list
            self.patients[patient_id].test_records = updated_records

            # Save the updated records
            self.save_records()

            if record_found:
                print("Record deleted successfully.")
            else:
                print("No matching record found.")
        else:
            print("Patient ID not found.")

    #def search_by_patient_id(self, patient_id):
    #   if patient_id in self.patients:
    #       return self.patients[patient_id].test_records
    #   return []

    # def search_up_normal_tests(self, test_name):
    # result = []
    # for patient in self.patients.values():
    #     for record in patient.test_records:
    #         if record['test_name'] == test_name:
    #             # Load normal ranges for the test
    #             file = open(self.test_file, 'r')
    #             try:
    #                 for line in file:
    #                     test_data = line.strip().split(';')
    #                     if test_data[0] == test_name:
    #                         normal_range = test_data[1]
    #                         break
    #             finally:
    #                 file.close()
    #             # Check if the result is abnormal
    #             normal_ranges = normal_range.split(',')
    #             is_up_normal = False
    #             for condition in normal_ranges:
    #                 operator = condition[0]
    #                 value = float(condition[1:])
    #                 if operator == '>' and float(record['result_value']) <= value:
    #                     is_up_normal = True
    #                     break
    #                 elif operator == '<' and float(record['result_value']) >= value:
    #                     is_up_normal = True
    #                     break
    #             if is_up_normal:
    #                 result.append(record)
    # return result

    def load_test_ranges(self, filename):
        test_ranges = {}
        try:
            with open(filename, 'r') as file:
                for line in file:
                    parts = line.strip().split(';')
                    if len(parts) == 4:
                        test_name = parts[0].strip()
                        range_values = parts[1].strip()
                        unit = parts[2].strip()
                        # date is not used in this implementation
                        # date = parts[3].strip()

                        # Initialize min_range and max_range as None
                        min_range, max_range = None, None

                        # Parse the range values
                        if '>' in range_values:
                            min_part = range_values.split(',')[0].strip()
                            if '>' in min_part:
                                min_range = float(min_part.split('>')[1].strip())

                        if '<' in range_values:
                            max_part = range_values.split(',')[-1].strip()  # Ensure we get the last part
                            if '<' in max_part:
                                max_range = float(max_part.split('<')[1].strip())

                        # Store test ranges in the dictionary
                        test_ranges[test_name] = {
                            'min_range': min_range,
                            'max_range': max_range,
                            'unit': unit
                        }
                    else:
                        print(f"Warning: Skipping unwanted lines: {line.strip()}")
            return test_ranges
        except IOError:
            print("Error reading test ranges from the file.")
            return {}

    def filter_medical_tests(self, return_records=False):
        print("\nFilter Medical Tests - Options:")
        print("1. Filter by Patient ID")
        print("2. Filter by Test Name")
        print("3. Filter by Abnormal Tests")
        print("4. Filter by Date Range")
        print("5. Filter by Test Status")
        print("6. Filter by Turnaround Time Range")

        # Collect user choices for each filter
        filter_options = {
            'patient_id': int(input("Apply Filter by Patient ID? (1/0): ")),
            'test_name': int(input("Apply Filter by Test Name? (1/0): ")),
            'abnormal_tests': int(input("Apply Filter by Abnormal Tests? (1/0): ")),
            'date_range': int(input("Apply Filter by Date Range? (1/0): ")),
            'test_status': int(input("Apply Filter by Test Status? (1/0): ")),
            'turnaround_time': int(input("Apply Filter by Turnaround Time Range? (1/0): "))
        }

        # Initialize variables for filter inputs
        patient_id = test_name = status = None
        start_date = end_date = None
        min_time = max_time = None

        # Gather filter inputs based on user choices
        if filter_options['patient_id']:
            patient_id = input("Enter Patient ID: ").strip()

        if filter_options['test_name']:
            test_name = input("Enter Test Name: ").strip()

        if filter_options['date_range']:
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()

        if filter_options['test_status']:
            status = input("Enter Test Status: ").strip()

        if filter_options['turnaround_time']:
            min_time = float(input("Enter minimum turnaround time (in minutes): ").strip())
            max_time = float(input("Enter maximum turnaround time (in minutes): ").strip())

        filtered_records = []

        # Iterate through each patient and their records once
        for patient in self.patients.values():
            for record in patient.test_records:
                # Start with the assumption that the record matches all conditions
                matches = True

                # Apply each filter
                if filter_options['patient_id'] and patient_id and patient.patient_id != patient_id:
                    matches = False

                if filter_options['test_name'] and test_name and record.get('test_name') != test_name:
                    matches = False

                if filter_options['abnormal_tests']:
                    test_ranges = self.load_test_ranges('medicalTest.txt')
                    test_name_in_record = record.get('test_name')
                    result_value = record.get('result_value')
                    if test_name_in_record and result_value:
                        try:
                            result_value = float(result_value)
                            if test_name_in_record in test_ranges:
                                min_range = test_ranges[test_name_in_record]['min_range']
                                max_range = test_ranges[test_name_in_record]['max_range']
                                if not ((min_range is not None and result_value < min_range) or
                                        (max_range is not None and result_value > max_range)):
                                    matches = False
                        except ValueError:
                            print(f"Invalid result value for test '{test_name_in_record}' in record: {record}")
                            matches = False
                    else:
                        matches = False

                if filter_options['date_range'] and start_date and end_date:
                    test_date = record.get('test_date_time', '')[:10]
                    if not (start_date <= test_date <= end_date):
                        matches = False

                if filter_options['test_status'] and status and record.get('status') != status:
                    matches = False

                if filter_options['turnaround_time'] and min_time is not None and max_time is not None:
                    try:
                        turnaround_time = float(record.get('turnaround_time', 0))
                        if not (min_time <= turnaround_time <= max_time):
                            matches = False
                    except ValueError:
                        print(f"Invalid turnaround time for record: {record}")
                        matches = False

                # If all conditions match, add the record
                if matches:
                    # Include patient ID in each record for display or return
                    record_with_patient_id = record.copy()  # Copy the record to avoid modifying the original
                    record_with_patient_id['patient_id'] = patient.patient_id  # Add patient ID to the record
                    filtered_records.append(record_with_patient_id)

        # Return or display the filtered records
        if return_records:
            return filtered_records
        else:
            if filtered_records:
                self.display_records(filtered_records)
            else:
                print("No matching records found.")

    def display_records(self, records):
        if records:
            for record in records:
                # Print each record's details
                print(f"Patient ID: {record.get('patient_id', 'N/A')}, "
                      f"Test Name: {record.get('test_name', 'N/A')}, "
                      f"Date/Time: {record.get('test_date_time', 'N/A')}, "
                      f"Result: {record.get('result_value', 'N/A')}, "
                      f"Unit: {record.get('unit', 'N/A')}, "
                      f"Status: {record.get('status', 'N/A')}, "
                      f"Result Date/Time: {record.get('result_date_time', 'N/A')}")
        else:
            print("No records found matching the criteria.")

    def calculate_turnaround_time(self, record):
        """Calculate turnaround time in minutes based on test and result dates."""
        test_date_str = record.get('test_date_time', '')
        result_date_str = record.get('result_date_time', '')

        # Check if both date-time strings are valid and not empty
        if test_date_str and result_date_str:
            try:
                # Parse the date-time strings into datetime objects
                test_date = datetime.strptime(test_date_str, "%Y-%m-%d %H:%M")
                result_date = datetime.strptime(result_date_str, "%Y-%m-%d %H:%M")

                # Calculate turnaround time in minutes
                turnaround_time = (result_date - test_date).total_seconds() / 60
                return turnaround_time
            except ValueError:
                print(f"Skipping record due to invalid date format: {record}")
                return None
        else:
            print(f"Skipping record due to missing date information: {record}")
            return None

    def generate_summary_report(self, records):
        """Generate descriptive statistics for the filtered records."""
        if not records:
            print("No records found for the summary report.")
            return

        # Initialize variables for statistics
        result_values = []
        turnaround_times = []

        # Extract relevant data from records
        for record in records:
            if 'result_value' in record and record['result_value'] is not None:
                try:
                    result_values.append(float(record['result_value']))
                except ValueError:
                    print(f"Skipping record due to invalid result value: {record}")
                    continue  # Skip invalid result values

            turnaround_time = self.calculate_turnaround_time(record)
            if turnaround_time is not None:
                turnaround_times.append(turnaround_time)

        # Compute statistics for result values
        if result_values:
            min_value = min(result_values)
            max_value = max(result_values)
            avg_value = sum(result_values) / len(result_values)
            print(f"\nTest Value Statistics:")
            print(f"Minimum Value: {min_value}")
            print(f"Maximum Value: {max_value}")
            print(f"Average Value: {avg_value:.2f}")
        else:
            print("No valid test result values found.")

        # Compute statistics for turnaround times
        if turnaround_times:
            min_turnaround = min(turnaround_times)
            max_turnaround = max(turnaround_times)
            avg_turnaround = sum(turnaround_times) / len(turnaround_times)
            print(f"\nTurnaround Time Statistics (in minutes):")
            print(f"Minimum Turnaround Time: {min_turnaround}")
            print(f"Maximum Turnaround Time: {max_turnaround}")
            print(f"Average Turnaround Time: {avg_turnaround:.2f}")
        else:
            print("No valid turnaround times found.")

    def generate_summary_report_option(self):
        filtered_records = self.filter_medical_tests(return_records=True)
        self.generate_summary_report(filtered_records)

    def print_all_records(self):
        if not self.patients:
            print("No records found.")
            return
        for patient_id, patient in self.patients.items():
            print(f"\nPatient ID: {patient_id}")
            for record in patient.test_records:
                print(f"  Test Name: {record['test_name']}")
                print(f"  Test Date & Time: {record['test_date_time']}")
                print(f"  Result Value: {record['result_value']} {record['unit']}")
                print(f"  Status: {record['status']}")
                if record['result_date_time']:
                    print(f"  Result Date & Time: {record['result_date_time']}")
                print()  # Add a blank line between records for clarity

    def validate_range_values(self,range_values):
        #Validates the range values. Ensures they are in the correct format (e.g., '> 13.8, < 17.2').

            # Remove any leading/trailing whitespace
            range_values = range_values.strip()

            # Split the string by a comma (if present) to handle up to two conditions
            conditions = range_values.split(',')

            # We can only have one or two conditions
            if len(conditions) > 2:
                print("Invalid range values: Too many conditions.")
                return False

            # Validate each condition
            for condition in conditions:
                # Strip any whitespace from the condition
                condition = condition.strip()

                # Check if the condition starts with a valid operator
                if condition.startswith(('>=', '<=', '>', '<')):
                    operator = condition[:2] if condition[:2] in ('>=', '<=') else condition[:1]
                    number_str = condition[len(operator):].strip()

                    # Check if the remaining part is a valid number
                    try:
                        float(number_str)  # Try to convert to a float
                    except ValueError:
                        print(f"Invalid range value: '{number_str}' is not a number.")
                        return False
                else:
                    print(f"Invalid range value: '{condition}' does not start with a valid operator.")
                    return False

            # If all conditions are valid
            return True

    def validate_unit(self,unit):
        #Validates the unit. Ensures it is not empty and in the expected format.
        if not unit.strip():
            print("Unit cannot be empty.")
            return False
        elif unit.isdigit():
            print("Unit cannot has digite.")
            return False
        return True


    def validate_turnaround_time(self,turnaround_time):
        #Validates the turnaround time. Ensures it is in the correct format DD-hh-mm
        #and that days, hours, and minutes are valid.
        try:
            days, hours, minutes = turnaround_time.split('-')
            if int(days) < 0 or int(hours) < 0 or int(hours) > 23 or int(minutes) < 0 or int(minutes) > 59:
                print("Invalid turnaround time values. Please ensure hours are between 0-23 and minutes between 0-59.")
                return False
            return True
        except ValueError:
            print("Invalid turnaround time format. Please enter in the format DD-hh-mm.")
            return False

    def validate_test_name(self,test_name, existing_tests):
        # Validates the test name. Ensures it is not empty and not a duplicate.
        if not test_name.strip():
            print("Test name cannot be empty.")
            return False
        if test_name in existing_tests:
            print("Test name already exists.")
            return False
        return True

    def add_new_medical_test(self, existing_tests):
        test_name = input("Enter test name: ")
        if not self.validate_test_name(test_name, existing_tests):
            return

        range_values = input("Enter range values (e.g., '> 13.8, < 17.2'): ")
        if not self.validate_range_values(range_values):
            return

        unit = input("Enter unit: ")
        if not self.validate_unit(unit):
            return

        turnaround_time = input("Enter turnaround time (format DD-hh-mm): ")
        if not self.validate_turnaround_time(turnaround_time):
            return

        self.save_medical_test(test_name, range_values, unit, turnaround_time)
        print("Test added successfully!")

    def save_medical_test(self, test_name, range_values, unit, turnaround_time):
        try:
            file = open(self.test_file, 'a')  # Open the file in append mode
            try:
                file.write(f"{test_name}; {range_values}; {unit}; {turnaround_time}\n")
                print("Test added successfully.")
            finally:
                file.close()  # Make sure to close the file
        except IOError:
            print("Error saving the test to the file.")


    def update_medical_test(self, old_test_name, new_test_name, new_range_values, new_unit, new_turnaround_time):
        if not self.validate_test_name(new_test_name, self.tests):
            print("Invalid new test name. Update aborted.")
            return

        if not self.validate_range_values(new_range_values):
            print("Invalid new range values. Update aborted.")
            return

        if not self.validate_unit(new_unit):
            print("Invalid new unit. Update aborted.")
            return

        if not self.validate_turnaround_time(new_turnaround_time):
            print("Invalid new turnaround time. Update aborted.")
            return

        try:
            # Open the test file in read mode
            with open(self.test_file, 'r') as file:
                lines = file.readlines()

            # Flag to check if the test was found
            test_found = False

            # Prepare a list to hold updated lines
            updated_lines = []

            # Iterate through the lines to find and update the test
            for line in lines:
                parts = line.strip().split('; ')
                if parts[0] == old_test_name:
                    # Test found, prompt for new details
                    test_found = True
                    # Prepare the updated line
                    updated_line = f"{new_test_name}; {new_range_values}; {new_unit}; {new_turnaround_time}\n"
                    updated_lines.append(updated_line)
                else:
                    # Keep the line as is if it doesn't match the old test name
                    updated_lines.append(line)

            # Open the test file in write mode to overwrite the content
            with open(self.test_file, 'w') as file:
                file.writelines(updated_lines)

            if test_found:
                print("Medical test updated successfully.")
            else:
                print("Test not found. No updates made.")

        except IOError:
            print("Error handling the file.")

    def import_records(self, filename):
        try:
            with open(filename, 'r') as file:
                for line in file:
                    row = line.strip().split(',')

                    # Ensure that there are enough fields in the row
                    if len(row) != 7 :
                        print(f"Skipping wrong formatted line: {line}")
                        continue

                    # Unpack the fields
                    patient_id= row[0]
                    #print(patient_id)
                    test_name= row[1]
                    #print(test_name)
                    test_date_time= row[2]
                    #print(test_date_time)
                    result_value= row[3]
                    #print(result_value)
                    unit= row[4]
                    #print(unit)
                    status= row[5]
                    #print(status)
                    result_date_time = row[6]
                    #print(result_date_time)

                    # If the patient_id is not in the system, create a new Patient object
                    if patient_id not in self.patients:
                        self.patients[patient_id] = Patient(patient_id)

                    # Add the test record to the patient
                    self.patients[patient_id].add_test_record(
                        test_name, test_date_time, result_value, unit, status,
                        result_date_time if result_date_time else None
                    )

            # Save the records after importing
            self.save_records()
            print("Records imported successfully.")

        except IOError:
            print("Error importing records from the file.")

    def export_records(self, filename):
        try:
            with open(filename, 'w') as file:
                # Write the header line explaining each field
                header = (
                    "Patient ID,Test Name,Test Date and Time,Result Value,"
                    "Unit,Status,Result Date and Time"
                )
                file.write(header + '\n')

                for patient in self.patients.values():
                    for record in patient.test_records:
                        # Prepare the line for export
                        line = (
                            f"{patient.patient_id},{record['test_name']},"
                            f"{record['test_date_time']},{record['result_value']},"
                            f"{record['unit']},{record['status']},"
                            f"{record['result_date_time'] if record['result_date_time'] else ''}"
                        )
                        # Write the line to the file
                        file.write(line + '\n')

                print("Records exported successfully.")
        except IOError:
            print("Error exporting records to the file.")


# def main():
system = MedicalTestSystem("medicalRecord.txt", "medicalTest.txt")
system.load_records()
system.load_test()
while True:
    print("\nMenu:")
    print("1.Add new medical test.")
    print("2.Add new medical test record.")
    print("3.Update patient record.")
    print("4.Update medical tests.")
    print("5.Delete patient record.")
    print("6.Filter medical tests.")
    print("7.Generate textual summary reports.")
    print("8.Export medical records.")
    print("9.Import medical records.")
    print("10.Print all records.")
    print("11.Exit.")

    try:
        choice = int(input("Choose an option: "))
        if choice == 1:
            system.add_new_medical_test(system.tests)

        elif choice == 2:
            print("Adding a new test record:")

            # Validate Patient ID
            while True:
                patient_id = input("Patient ID (7 digits): ")
                if not patient_id.isdigit():
                    print("Invalid Patient ID. It should consist of digits only.")
                elif len(patient_id) != 7:
                    print("Invalid Patient ID. It should be exactly 7 digits.")
                else:
                    break

            # Validate Test Name
            while True:
                test_name = input("Test Name (fixed length): ")
                if not test_name:
                    print("Invalid Test Name. It cannot be empty.")
                elif not system.is_valid_test_name(test_name):
                    print("Invalid Test Name. It should not exceed the maximum length.")
                else:
                    break

            # Validate Test Date and Time
            while True:
                test_date_time = input("Test Date and Time (YYYY-MM-DD HH:MM): ")
                if not system.is_valid_date_time(test_date_time):
                    # The method already provides specific error messages
                    continue
                else:
                    break

            # Validate Result Value
            while True:
                result_value = input("Result Value (numeric): ")
                if not system.is_valid_numeric(result_value):
                    print("Invalid Result Value. It should be a numeric value.")
                else:
                    break

            # Validate Unit
            while True:
                unit = input("Results Unit (fixed length): ")
                if not unit.strip():
                    print("Invalid Results Unit. It cannot be empty.")
                elif not system.is_valid_unit(unit):
                    print("Invalid Results Unit. It should not exceed the maximum length.")
                else:
                    break

            # Validate Status
            while True:
                status = input("Status (Pending, Completed, Reviewed): ")
                if not system.is_valid_status(status):
                    print("Invalid Status. It should be one of 'Pending', 'Completed', 'Reviewed'.")
                else:
                    break

            # Validate Result Date and Time if Status is Completed
            result_date_time = None
            if status == "Completed":
                while True:
                    result_date_time = input("Result Date and Time (YYYY-MM-DD HH:MM, leave blank if not applicable): ")
                    if result_date_time == "":
                        result_date_time = None
                        break
                    elif not system.is_valid_date_time(result_date_time):
                        print("Invalid Result Date and Time format. Please use YYYY-MM-DD HH:MM.")
                    else:
                        break

            # Add the test record
            system.add_test_record(patient_id, test_name, test_date_time, result_value, unit, status, result_date_time)

        elif choice == 3:
            while True:
                patient_id = input("Patient ID: ")
                if patient_id not in system.patients:
                    print("Patient ID does not exist. Please enter a valid Patient ID.")
                else:
                    break

            while True:
                test_name = input("Test Name to Update: ")
                # Check if the patient has a record with the given test name
                if not any(record['test_name'] == test_name for record in system.patients[patient_id].test_records):
                    print("Test Name not found for this Patient ID. Please enter a valid Test Name.")
                else:
                    break

            print("Enter new values (leave blank to keep the old value):")

            # Collect and validate new values
            while True:
                test_date_time = input("New Test Date Time (YYYY-MM-DD HH:MM, leave blank if not applicable): ")
                if test_date_time and not system.is_valid_date_time(test_date_time):
                    print("Invalid Test Date and Time format. Please use YYYY-MM-DD HH:MM.")
                else:
                    break

            while True:
                result_value = input("New Result Value (numeric, leave blank if not applicable): ")
                if result_value and not system.is_valid_numeric(result_value):
                    print("Invalid Result Value. It should be a numeric value.")
                else:
                    break

            while True:
                unit = input("New Unit (leave blank if not applicable): ")
                if unit and not system.is_valid_unit(unit):
                    print("Invalid Unit. It should not exceed the maximum length.")
                else:
                    break

            while True:
                status = input("New Status (Pending, Completed, Reviewed, leave blank if not applicable): ")
                if status and not system.is_valid_status(status):
                    print("Invalid Status. It should be one of 'Pending', 'Completed', 'Reviewed'.")
                else:
                    break

            while True:
                result_date_time = input("New Result Date Time (YYYY-MM-DD HH:MM, leave blank if not applicable): ")
                if result_date_time and not system.is_valid_date_time(result_date_time):
                    print("Invalid Result Date and Time format. Please use YYYY-MM-DD HH:MM.")
                else:
                    break

            kwargs = {}
            if test_date_time:
                kwargs['test_date_time'] = test_date_time
            if result_value:
                kwargs['result_value'] = result_value
            if unit:
                kwargs['unit'] = unit
            if status:
                kwargs['status'] = status
            if result_date_time:
                kwargs['result_date_time'] = result_date_time

            system.update_test_record(patient_id, test_name, **kwargs)


        elif choice == 4:
            old_test_name = input("Enter the old test name to update: ")
            new_test_name = input("Enter the new test name: ")
            new_range_values = input("Enter the new range (e.g., > 13.8, < 17.2): ")
            new_unit = input("Enter the new unit: ")
            new_turnaround_time = input("Enter the new turnaround time (e.g., 00-03-04): ")
            system.update_medical_test(old_test_name, new_test_name, new_range_values, new_unit, new_turnaround_time)

        elif choice == 5:
            patient_id = input("Enter the Patient ID: ")
            test_name = input("Enter the Test Name: ")
            test_date_time = input("Enter the Test Date and Time (YYYY-MM-DD HH:MM:SS): ")
            result_value = input("Enter the Result Value: ")
            unit = input("Enter the Unit: ")
            status = input("Enter the Status: ")
            result_date_time = input(
                "Enter the Result Date and Time (YYYY-MM-DD HH:MM:SS) or leave blank if not applicable: ")

            # Delete the record
            system.delete_record(patient_id, test_name, test_date_time, result_value, unit, status, result_date_time)

        elif choice == 6:
            system.filter_medical_tests()

        elif choice == 7:
            system.generate_summary_report_option()

        elif choice == 8:
            filename = input("Enter filename to export records: ")
            system.export_records(filename)

        elif choice == 9:
            filename = input("Enter filename to import records: ")
            system.import_records(filename)

        elif choice == 10:
            system.print_all_records()
        elif choice == 11:
            break
        else:
            print("Invalid option!")
    except ValueError:
        print("Please enter a valid number.")

# Run the user management system 