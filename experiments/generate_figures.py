import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_architecture():
    os.makedirs('paper/figures', exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    # Simple blocks for architecture
    boxes = [
        {'xy': (0.1, 0.4), 'w': 0.2, 'h': 0.2, 'label': 'Frontend\n(Farmer/Consumer Dashboard)'},
        {'xy': (0.4, 0.6), 'w': 0.2, 'h': 0.2, 'label': 'Django App\n(Marketplace/Orders)'},
        {'xy': (0.4, 0.2), 'w': 0.2, 'h': 0.2, 'label': 'Django App\n(ai_services)'},
        {'xy': (0.7, 0.4), 'w': 0.2, 'h': 0.2, 'label': 'PostgreSQL\nDatabase'}
    ]
    
    for b in boxes:
        ax.add_patch(patches.Rectangle(b['xy'], b['w'], b['h'], fill=True, color='lightblue', ec='black'))
        ax.text(b['xy'][0] + b['w']/2, b['xy'][1] + b['h']/2, b['label'], ha='center', va='center', fontsize=10)
        
    ax.annotate('', xy=(0.4, 0.7), xytext=(0.3, 0.5), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate('', xy=(0.4, 0.3), xytext=(0.3, 0.5), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate('', xy=(0.7, 0.5), xytext=(0.6, 0.7), arrowprops=dict(arrowstyle="<->", lw=1.5))
    ax.annotate('', xy=(0.7, 0.5), xytext=(0.6, 0.3), arrowprops=dict(arrowstyle="<->", lw=1.5))
    
    plt.title("UzhavarHub System Architecture")
    plt.savefig('paper/figures/architecture.png', bbox_inches='tight')
    plt.close()

def generate_pipeline():
    os.makedirs('paper/figures', exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.axis('off')
    
    boxes = [
        {'xy': (0.05, 0.4), 'w': 0.2, 'h': 0.2, 'label': 'Data Collection\n(Soil, Weather, E-com)'},
        {'xy': (0.35, 0.4), 'w': 0.2, 'h': 0.2, 'label': 'Preprocessing\n(Cleaning, Joining)'},
        {'xy': (0.65, 0.65), 'w': 0.25, 'h': 0.15, 'label': 'Classification (Crop Rec)\nRandomForest'},
        {'xy': (0.65, 0.4), 'w': 0.25, 'h': 0.15, 'label': 'Regression (Demand/Weather)'},
        {'xy': (0.65, 0.15), 'w': 0.25, 'h': 0.15, 'label': 'Regression (Dynamic Pricing)\nRandomForest'}
    ]
    
    for b in boxes:
        ax.add_patch(patches.Rectangle(b['xy'], b['w'], b['h'], fill=True, color='lightgreen', ec='black'))
        ax.text(b['xy'][0] + b['w']/2, b['xy'][1] + b['h']/2, b['label'], ha='center', va='center', fontsize=9)
        
    ax.annotate('', xy=(0.35, 0.5), xytext=(0.25, 0.5), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate('', xy=(0.65, 0.725), xytext=(0.55, 0.5), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate('', xy=(0.65, 0.475), xytext=(0.55, 0.5), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate('', xy=(0.65, 0.225), xytext=(0.55, 0.5), arrowprops=dict(arrowstyle="->", lw=1.5))
    
    plt.title("UzhavarHub ML Pipeline")
    plt.savefig('paper/figures/pipeline.png', bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    generate_architecture()
    generate_pipeline()
    print("Figures generated.")
