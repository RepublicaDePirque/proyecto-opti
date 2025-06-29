import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


#Graph generating function
def plots_generate():
    x = ['small_t_1', 'small_t_2', 'medium_t_1', 'medium_t_2', 'large_t_1', 'large_t_2']
    y_of = [30834.0474040404, 31478.3084141414, 60047.046967676, 72467.5619979798, 284893.537482828, 333093.001845455]
    y_time = [0.014, 0.013, 0.072, 0.174, 3.028, 4.228]  
    
    plt.figure(figsize=(10, 6))
    plt.bar(x, y_of, color='skyblue')
    plt.xlabel('Tamaño Instancia', fontsize=12)
    plt.ylabel('Costo Total', fontsize=12)
    plt.title('Costo Total de la Red por Instancia', fontsize=14)
    plt.savefig('of_values.png', dpi=300, bbox_inches='tight')
    
    plt.figure(figsize=(10, 6))
    plt.bar(x, y_time, color='skyblue')
    plt.xlabel('Tamaño Instancia', fontsize=12)
    plt.ylabel('Costo Total', fontsize=12)
    plt.title('Costo Total de la Red por Instancia', fontsize=14)
    plt.savefig('time_values.png', dpi=300, bbox_inches='tight')
if __name__ == "__main__":
    plots_generate()