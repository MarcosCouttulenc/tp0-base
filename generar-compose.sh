archivo_salida=$1
cantidad_clientes=$2

echo "Nombre del archivo de salida: $archivo_salida"
echo "Cantidad de clientes: $cantidad_clientes"

python3 generador-de-compose.py "$archivo_salida" "$cantidad_clientes"
