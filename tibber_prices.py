import datetime
import os
import requests
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def get_api_key():
    api_key = os.getenv('TIBBER_API_KEY')
    if not api_key:
        raise ValueError("API-Key nicht gefunden. Bitte setzen Sie die Umgebungsvariable TIBBER_API_KEY.")
    return api_key

def find_minimal_sum_hours(prices, count):
    min_sum = float('inf')
    min_sum_indices = []
    min_start = 0

    for i in range(len(prices) - (count - 1)):
        current_sum = sum(prices[i:i + count])
        if current_sum < min_sum:
            min_sum = current_sum
            min_start = i

    for c in range(count):
        min_sum_indices.append(min_start + c)

    return min_sum_indices

def generate_plot(pricedata, total_min_price, total_max_price, label = 'heute', alpha=1.0):
    hours = [item[0].split('T')[1][:2] for item in pricedata]
    costs = [float(item[1]) for item in pricedata]

    # Extrahiere Zeitstempel und Preise
    timestamps, prices = zip(*pricedata)

    # Erstelle einen linearen Farbverlauf
    cmap = LinearSegmentedColormap.from_list('custom_colormap', ['green', 'yellow', 'red', '#800000'], N=256)

    fig, ax = plt.subplots(1, 1, figsize=(10, 12), sharex=True)

    # Plotte Balken mit individuellen Farben
    (min_price, max_price) = min(prices), max(prices)
    color = [cmap((price - total_min_price) / (total_max_price - total_min_price)) for price in prices]
    ax.bar(timestamps, prices, color=color, label=label)

    minimal_sum_hours = find_minimal_sum_hours(prices, 4)
    for index in minimal_sum_hours:
        ax.patches[index].set_edgecolor('blue')
        ax.patches[index].set_linewidth(4)

    # Balken für die aktuelle Stunde hervorheben
    if (label == "heute"):
        current_hour = datetime.datetime.now().hour
        ax.patches[current_hour].set_edgecolor('black')
        ax.patches[current_hour].set_linewidth(2)

    # Setze die Y-Achse mit einem Minimalwert unterhalb des absoluten Minimums
    min_y_value = min_price - 0.1 * min_price
    max_y_value = max_price + 0.025 * max_price
    ax.set_ylim(min_y_value, max_y_value)

    # Füge Achsentitel hinzu
    ax.set_xlabel('Stunde')
    ax.set_ylabel('Strompreis')
    ax.set_title('Stündliche Strompreise %s (Min: %2.1f, Max: %2.1f, Durchschnitt: %2.1f)' %
                 (label, 100 * min_price, 100 * max_price, 100 * sum(prices) / len(prices)))

    # Setze die X-Achsenlinien als einfache Stundenzahlen
    ax.set_xticks(range(24))
    ax.set_xticklabels([str(hour) for hour in range(24)])

    # Zeichne horizontale Linien hinter den Balken für jeden Y-Achsentick
    y_ticks = ax.get_yticks()
    for tick in y_ticks:
        ax.axhline(tick, color='lightgrey', linestyle='--', linewidth=0.7)

    # Setze die Breite des PNG-Diagramms auf 1920 Pixel
    plt.gcf().set_size_inches(19.0, 5.0)

    # Speichere Diagramm als PNG-Datei
    plt.savefig('strompreise_diagramm_%s.png' % label)


api_key = get_api_key()
api_url = 'https://api.tibber.com/v1-beta/gql?query=query{viewer{homes{currentSubscription{priceInfo{today{total startsAt}tomorrow{total startsAt}}}}}}'

response = requests.get(api_url, headers={'Authorization': 'Bearer %s' % api_key})

if response.status_code == 200:
    data = response.json()
    today_data = [(item['startsAt'], item['total']) for item in data['data']['viewer']['homes'][0]['currentSubscription']['priceInfo']['today']]
    has_tomorrow = False
    try:
        tomorrow_data = [(item['startsAt'], item['total']) for item in data['data']['viewer']['homes'][0]['currentSubscription']['priceInfo']['tomorrow']]
        has_tomorrow = True
    except Exception as e:
        tomorrow_data = today_data

    all_data = list(map(lambda x: x[1], today_data)) + list(map(lambda x: x[1], tomorrow_data))
    all_min = min(all_data)
    all_max = max(all_data)

    generate_plot(today_data, all_min, all_max, 'heute')
    if has_tomorrow:
        generate_plot(tomorrow_data, all_min, all_max, 'morgen')

else:
    print(f"Fehler bei der API-Anfrage. Statuscode: {response.status_code}")
    print(response.text)
