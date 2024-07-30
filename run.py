import os
import subprocess
import sys

log_file_path = "deletion_errors.log"

def log_error(message):
	with open(log_file_path, 'a', encoding='utf-8') as log_file:
		log_file.write(message + '\n')
def print_progress(processed, total):
	progress = processed / total
	bar_length = 40
	block = int(round(bar_length * progress))
	progress_text = f"\rProgress: [{'#' * block + '-' * (bar_length - block)}] {round(progress * 100, 2)}%"
	print(progress_text, end='')
def GrantFullAdmin(file_path):
	try:
		command = f'icacls "{file_path}" /grant Administrators:F /T /C /Q'
		result = subprocess.run(command, shell=True, capture_output=True, text=True)
		if result.returncode == 0:
			return True
		else:
			log_message = result.stderr.decode('utf-8', errors='replace')
			log_error(f"Error granting Administrators permissions on '{file_path}': {log_message}")
		#log_message = subprocess.check_output(command, shell=True).decode('utf-8', errors='replace')
		#if "Failed processing 0 files" in log_message:
			#return True
		#else:
			#log_error(f"Granting permissions {file_path}: {log_message}")
	except Exception as e:
		log_error(f"Failed to granting permissions for {file_path}: {e}")
	return False
def TakeOwnership(file_path):
	# f'takeown /F "{file_path}" /R /D Y'
	try:
		command = f'takeown /F "{file_path}"'
		result = subprocess.run(command, shell=True, capture_output=True, text=True)
		if result.returncode == 0:
			return True
		else:
			log_message = result.stderr.decode('utf-8', errors='replace')
			log_error(f"Error taking ownership on '{file_path}': {log_message}")
		#log_message = subprocess.check_output(command, shell=True).decode('utf-8', errors='replace')
		#if "SUCCESS:" in log_message or "CORRECTO:" in log_message:
			#return True
		#else:
			#log_error(f"Ownership {file_path}: {log_message}")
	except Exception as e:
		log_error(f"Failed to take ownership for {file_path}: {e}")
	return False
def AddUser(file_path):
	try:
		command = f'icacls "{file_path}" /grant "%USERNAME%":(OI)(CI)F'
		#log_message = subprocess.check_output(command, shell=True).decode('utf-8', errors='replace')
		result = subprocess.run(command, shell=True, capture_output=True, text=True)
		if result.returncode == 0:
			return True
		else:
			log_message = result.stderr.decode('utf-8', errors='replace')
			log_error(f"Error adding user on '{file_path}': {log_message}")
		#if "SUCCESS:" in log_message or "CORRECTO:" in log_message:
			#return True
		#else:
			#log_error(f"Add User {file_path}: {log_message}")
	except Exception as e:
		log_error(f"Failed to take add user for {file_path}: {e}")
	return False
def ProcessDirectoryPermissions(directory):
	processed_items = 0
	if not os.path.exists(directory):
		log_error(f"The specified path does not exist: {directory}")
		print(f"The specified path does not exist: {directory}")
	
	all_items = []
	for root, dirs, files in os.walk(directory, topdown=False):
		for file in files:
			all_items.append(os.path.join(root, file))
		for dir in dirs:
			all_items.append(os.path.join(root, dir))
	all_items.append(directory)
	
	total_items = len(all_items)
	for root, dirs, files in os.walk(directory, topdown=False):
		for file in files:
			if file == log_file_path:
				continue
			file_path = os.path.join(root, file)
			own = TakeOwnership(file_path)
			granted = GrantFullAdmin(file_path)
			added = AddUser(file_path)
			if not own or not granted or not added:
				log_error(f"Failed to process file: {file_path}")
			else:
				own = TakeOwnership(root)
				granted = GrantFullAdmin(root)
				added = AddUser(root)
				if not own or not granted or not added:
					log_error(f"Failed to process root directory: {root}")
				own = TakeOwnership(file_path)
				granted = GrantFullAdmin(file_path)
				added = AddUser(file_path)
				if not own or not granted or not added:
					log_error(f"Failed to process file after root: {file_path}")
			
			processed_items += 1
			print_progress(processed_items, total_items)
		
		for dir in dirs:
			dir_path = os.path.join(root, dir)
			own = TakeOwnership(dir_path)
			granted = GrantFullAdmin(dir_path)
			added = AddUser(dir_path)
			if not own or not granted or not added:
				log_error(f"Failed to process directory: {dir_path}")
			processed_items += 1
			print_progress(processed_items, total_items)

current_dir = os.getcwd()
# directory = "G:\\FileOwnershipTool"
print("Current working directory:", current_dir)
ProcessDirectoryPermissions(current_dir)