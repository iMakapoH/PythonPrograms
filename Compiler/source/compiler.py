import os, sys, time, subprocess, psutil, shutil
import configparser, win32com.client

config = configparser.ConfigParser()
config_filename = 'settings.ini'

if not os.path.exists(os.path.join(os.getcwd(), config_filename)):
	config['FOLDERS'] = { 'server_folder' : '', 'scripting_folder' : '' }
	config['OTHER'] = { 'start_name' : '', 'auto_start' : '', 'auto_compiling' : '' }

	with open(config_filename, "w") as configfile:
		config.write(configfile)

	print('Конфиг создан! Настройте его.')

	time.sleep(3.0)
	sys.exit()

config.read(config_filename)

server_folder = config.get('FOLDERS', 'server_folder')
scripting_folder = config.get('FOLDERS', 'scripting_folder')
start_name = config.get('OTHER', 'start_name')
auto_start = bool(config.get('OTHER', 'auto_start'))
auto_compiling = bool(config.get('OTHER', 'auto_compiling'))

if start_name == '':
	auto_start = False
	print('Не указан файл запуска start_name!')

if not os.path.exists(server_folder):
	print('Директория server_folder не указана или не существует!')

	time.sleep(3.0)
	sys.exit()

if not os.path.exists(scripting_folder):
	print('Директория scripting_folder не указана или не существует!')

	time.sleep(3.0)
	sys.exit()

if auto_compiling == True:
	subprocess.call(r'cd {} & del compile.dat' .format(scripting_folder), shell = True)
	subprocess.Popen(os.path.join(scripting_folder, 'compile.exe'), cwd = scripting_folder)

	time.sleep(1.0)
	win32com.client.Dispatch("WScript.Shell").SendKeys('{ENTER}')

new_plugins_list = []
walk_data = []
plugins_ini = ''
auto_start_path = ''
compiled_folder = os.path.join(scripting_folder, 'compiled')

for path in os.walk(server_folder):
	walk_data.append(path)

for path, sub_path, file in walk_data:
	if path.find('plugins') != -1:
		for amxx_name in os.listdir(compiled_folder):
			new_plugins_list.append(amxx_name)

			plugin_path = os.path.join(path, amxx_name)

			if(os.path.isfile(plugin_path)):
				os.remove(plugin_path)

			shutil.move(os.path.join(compiled_folder, amxx_name), path)

for path, sub_path, file in walk_data:
	if path.find('configs') != -1:
		for file_name in file:
			if file_name == 'plugins.ini':
				plugins_ini = open(os.path.join(path, file_name), 'r+')

				for plugin_name in plugins_ini:
					for new_plugin in new_plugins_list:
						if plugin_name.rstrip() == new_plugin:
							new_plugins_list.remove(new_plugin)

	for file_name in file:
		if auto_start == True:
			if file_name == start_name:
				auto_start_path = path
		else:
			del auto_start_path

for new_plugin in new_plugins_list:
	plugins_ini.write('\n' + new_plugin)

plugins_ini.close()

if auto_start == True:
	for proc in psutil.process_iter():
		proc_info = proc.as_dict(['name'])

		if proc_info['name'] == 'hlds.exe':
			proc.kill()
			break

	subprocess.Popen(os.path.join(auto_start_path, start_name), cwd = auto_start_path)