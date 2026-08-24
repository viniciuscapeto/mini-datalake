import pyodbc

print("Drivers ODBC instalados na máquina:")
for driver in pyodbc.drivers():
    print(f" - {driver}")