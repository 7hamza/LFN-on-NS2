
#!/bin/bash

python 1.py
ns 1.tcl

for i in queues/*.tr
do
	echo "set terminal jpeg" >> my_plot.gps 
	echo "set output '$i.jpg'" >> my_plot.gps
    echo "plot '$i' u 1:5 w l title 'Q Size from $i'" >> my_plot.gps
    echo "reset" >> my_plot.gps
done

# call gnuplot
gnuplot my_plot.gps

# delete temporary file
rm my_plot.gps

for i in queues/*.tr
do
    echo "set terminal jpeg" >> my_plot.gps 
    echo "set output '$i_drops.jpg'" >> my_plot.gps
    echo "plot '$i' u 1:8 w l title 'Drops from $i'" >> my_plot.gps
    echo "reset" >> my_plot.gps
done

# call gnuplot
gnuplot my_plot.gps

# delete temporary file
rm my_plot.gps


for i in sinks/*.tr
do
	echo "set terminal jpeg" >> my_plot.gps 
	echo "set output '$i.jpg'" >> my_plot.gps
    echo "plot '$i' u 1:2 w l title 'data from $i'" >> my_plot.gps
    echo "reset" >> my_plot.gps
done

# call gnuplot
gnuplot my_plot.gps

# delete temporary file
rm my_plot.gps


for i in outs/*.tr
do
	echo "set terminal jpeg" >> my_plot.gps 
	echo "set output '$i.jpg'" >> my_plot.gps
    echo "plot '$i' u 1:2 w l title 'data from $i'" >> my_plot.gps
    echo "reset" >> my_plot.gps
done

# call gnuplot
gnuplot my_plot.gps

# delete temporary file
rm my_plot.gps