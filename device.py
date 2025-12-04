import subprocess
import json
import argparse
import logging

# Настройка логирования
logging.basicConfig(filename="device.log", level=logging.INFO, format='%(asctime)s - %(message)s')

# Функция для выполнения команд через ADB
def adb_command(command):
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {command}")
        logging.error(e.output.decode('utf-8'))
        return None

# Получение информации о системе
def get_system_info():
    system_info = {}
    
    # Получаем информацию о модели устройства
    system_info['Model'] = adb_command("adb shell getprop ro.product.model")
    
    # Получаем информацию о версии ОС
    system_info['OS Version'] = adb_command("adb shell getprop ro.build.version.release")
    
    # Получаем номер сборки
    system_info['Build Number'] = adb_command("adb shell getprop ro.build.display.id")
    
    # Получаем информацию о процессоре
    system_info['Processor'] = adb_command("adb shell cat /proc/cpuinfo | grep 'Processor' | head -n 1")
    
    # Получаем информацию о памяти
    memory_info = adb_command("adb shell dumpsys meminfo")
    if memory_info:
        system_info['Memory'] = memory_info.split("\n")[0]  # Можно дополнительно парсить для более точных данных
    
    # Получаем информацию о заряде батареи
    battery_info = adb_command("adb shell dumpsys battery")
    if battery_info:
        system_info['Battery'] = battery_info.split("\n")[0]  # Парсим только первую строку для краткости

    # Получаем информацию о сети
    system_info['Network'] = adb_command("adb shell dumpsys wifi | grep 'Wi-Fi'") or "No Wi-Fi connection"
    
    return system_info

# Получение информации об установленных приложениях
def get_installed_apps():
    apps = []
    result = adb_command("adb shell pm list packages -f")
    if result:
        for line in result.split("\n"):
            path, package = line.split("=", 1)
            apps.append({
                "Package": package,
                "Path": path
            })
    return apps

# Вывод информации в формате JSON
def export_to_json(data, filename="device_info.json"):
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data exported to {filename}")

# Функция для вывода информации
def print_info(system_info, apps_info):
    print("\nSystem Information:")
    for key, value in system_info.items():
        print(f"{key}: {value}")
    
    print("\nInstalled Apps:")
    for app in apps_info:
        print(f"Package: {app['Package']} - Path: {app['Path']}")

# Основная функция
def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description="Get detailed information about Android device via ADB.")
    
    parser.add_argument('--json', action='store_true', help='Export information to a JSON file')
    parser.add_argument('--system', action='store_true', help='Get system information')
    parser.add_argument('--apps', action='store_true', help='Get installed apps list')
    parser.add_argument('--battery', action='store_true', help='Get battery information')
    parser.add_argument('--log', action='store_true', help='Enable logging to file')

    args = parser.parse_args()

    if args.log:
        logging.info("Script started")

    # Проверка наличия устройства
    device_check = adb_command("adb devices")
    if not device_check or "device" not in device_check:
        print("No devices connected. Please connect a device via ADB.")
        return
    
    # Сбор информации
    system_info = {}
    apps_info = []

    if args.system:
        system_info = get_system_info()
        print_info(system_info, apps_info)

    if args.apps:
        apps_info = get_installed_apps()
        print_info(system_info, apps_info)

    # Экспорт в JSON, если указано
    if args.json:
        export_to_json(system_info if args.system else apps_info)

    if args.log:
        logging.info("Script completed successfully")

# Запуск основного процесса
if __name__ == "__main__":
    main()