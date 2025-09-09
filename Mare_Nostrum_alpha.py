import random

commodities = {
    "grano": {"base_price": 10},
    "vino": {"base_price": 25},
    "olio": {"base_price": 30},
    "pesce": {"base_price": 15},
    "spezie": {"base_price": 80},
}

price_caps = {
    "grano": 20,
    "vino": 50,
    "olio": 60,
    "pesce": 40,
    "spezie": 200,
}

cities = {
    "Genova": {"inventory": {"grano": 60, "vino": 20}, "demand": {"grano":20, "vino":20, "olio":15, "pesce":20, "spezie": 80}},
    "Tunisi": {"inventory": {"spezie": 40, "olio": 25}, "demand": {"grano":40, "vino":10, "olio":25, "pesce":20, "spezie": 10}},
    "Costantinopoli": {"inventory": {"pesce": 70}, "demand": {"grano":30, "vino":30, "olio":10, "pesce":10, "spezie": 5}},
    "Alessandria": {"inventory": {"spezie": 50}, "demand": {"grano":40, "vino":40, "olio":10, "pesce":5, "spezie": 10}}
}

city_production = {
    "Genova": ["olio", "pesce"],
    "Costantinopoli": ["vino", "grano"],
    "Tunisi": ["grano", "olio"],
    "Alessandria": ["spezie", "pesce"],
}

travel_times = {
    ("Genova", "Tunisi"): 3,
    ("Genova", "Costantinopoli"): 7,
    ("Genova", "Alessandria"): 9,
    ("Tunisi", "Genova"): 3,
    ("Tunisi", "Costantinopoli"): 6,
    ("Tunisi", "Alessandria"): 4,
    ("Costantinopoli", "Genova"): 7,
    ("Costantinopoli", "Tunisi"): 6,
    ("Costantinopoli", "Alessandria"): 5,
    ("Alessandria", "Genova"): 9,
    ("Alessandria", "Tunisi"): 4,
    ("Alessandria", "Costantinopoli"): 5,
}

neutral_stocks = {
    "grano": 50,
    "vino": 30,
    "olio": 20,
    "pesce": 30,
    "spezie": 10,
}

neutral_demands = {
    "grano": 20,
    "vino":20,
    "olio": 15,
    "pesce": 10,
    "spezie": 5,
}


player = {
    "location": "Genova",
    "cargo": {},
    "gold": 500,
    "capacity": 100,
    "in_viaggio": False,
    "destinazione": None,
    "giorni_rimanenti": 0
}

spread = 0.1 #differenza tra prezzo buy e sell
fee_rate = 0.05

#-------------------------#

def calculate_price(city, commodity, price_volatility=0.0):
    base = commodities[commodity]["base_price"]
    stock = city["inventory"].get(commodity, 0)
    demand = city["demand"].get(commodity, 0)
    
    modifier = 1 + (demand - stock) / 100
    market_price = max(1, int(base * modifier))
    
    if price_volatility > 0:
        volatility_amount = int(base * price_volatility)
        variation = random.randint(-volatility_amount, volatility_amount)
        market_price = max(1, market_price + variation)
        
    cap = price_caps.get(commodity)
    if cap is not None:
        market_price = min(market_price, cap)
    
    # Definiamo prezzi diversi per acquisto e vendita
    buy_price = int(market_price * (1+spread))   # paghi di più al mercato
    sell_price = int(market_price * (1-spread))  # il mercato paga meno
    
    return buy_price, sell_price

def buy(player, city_name, commodity, amount):
    city = cities[city_name]
    buy_price, _ = calculate_price(city, commodity)  # prendiamo il prezzo di acquisto
    
    if city["inventory"].get(commodity, 0) < amount:
        print("❌ Non abbastanza scorte in città.")
        return False
    
    total_cost = buy_price * amount
    if player["gold"] < total_cost:
        print("❌ Oro insufficiente.")
        return False
    
    if sum(player["cargo"].values()) + amount > player["capacity"]:
        print("❌ Nave troppo piena.")
        return False
    
    # aggiorna inventari
    city["inventory"][commodity] -= amount
    city["demand"][commodity] = city["demand"].get(commodity, 0) + amount
    player["cargo"][commodity] = player["cargo"].get(commodity, 0) + amount
    player["gold"] -= total_cost
    
    print(f"✅ Comprato {amount} di {commodity} a {buy_price} oro/unità.")
    return True

 
def sell(player, city_name, commodity, amount):
    city = cities[city_name]
    _, sell_price = calculate_price(city, commodity)  # prendiamo il prezzo di vendita
    
    if player["cargo"].get(commodity, 0) < amount:
        print("❌ Non hai abbastanza merce.")
        return False
    
    total_gain = sell_price * amount
    
    # aggiornamento inventari
    city["inventory"][commodity] = city["inventory"].get(commodity, 0) + amount
    city["demand"][commodity] = max(0, city["demand"].get(commodity, 0) - amount)
    player["cargo"][commodity] -= amount
    player["gold"] += total_gain
    
    print(f"✅ Venduto {amount} di {commodity} a {sell_price} oro/unità (Totale: {total_gain}).")
    return True


def travel_to(player, destination):
    if destination not in cities:
        print("Città non esistente.")
        return
    if player["location"] == destination:
        print("Sei già in quella città.")
        return

    key = (player["location"], destination)
    if key not in travel_times:
        print("Percorso non disponibile.")
        return

    durata = travel_times[key]
    player["in_viaggio"] = True
    player["destinazione"] = destination
    player["giorni_rimanenti"] = durata
    print(f"Partito da {player['location']} verso {destination}. Arrivo in {durata} turni.")

def update_market():
    for city_name, city in cities.items():
        for commodity in commodities:
            stock = city["inventory"].get(commodity, 0)
            demand = city["demand"].get(commodity, 0)
            
            neutral_stock = neutral_stocks.get(commodity, 50)  # valore di default 50 se non definito
            neutral_demand = neutral_demands.get(commodity, 50)

            # Autoregolazione dello stock
            if stock < neutral_stock:
                change = random.randint(0, 8)
            elif stock > neutral_stock:
                change = random.randint(-5, 0)
            else:
                change = random.randint(-3, 3)
            city["inventory"][commodity] = max(0, stock + change)

            # Autoregolazione della domanda
            if demand < neutral_demand:
                change = random.randint(0, 5)
            elif demand > neutral_demand:
                change = random.randint(-5, 0)
            else:
                change = random.randint(-1, 1)
            city["demand"][commodity] = max(0, demand + change)

def produce(city_name, production_multiplier=1.0):
    city = cities[city_name]
    for prod in city_production.get(city_name, []):
        base_production = random.randint(3,7)
        produced_amount = int(base_production * production_multiplier)
        city["inventory"][prod] = city["inventory"].get(prod, 0) + produced_amount
        print(f"{city_name} ha prodotto {produced_amount} unità di {prod}.")

def update_demand():
    for city_name, city in cities.items():
        for commodity in list(city["demand"].keys()):
            stock = city["inventory"].get(commodity, 0)
            demand = city["demand"][commodity]

            # Calcolo variazione base casuale (-5% a +5%)
            base_change = random.uniform(-0.05, 0.05)

            # Se lo stock è basso rispetto alla domanda, aumenta la domanda
            if stock < demand * 0.3:
                base_change += random.uniform(0.05, 0.15)  # aumento aggiuntivo

            # Calcolo nuova domanda
            new_demand = int(demand * (1 + base_change))
            city["demand"][commodity] = max(0, new_demand)

           
def show_status(player):
    city = cities[player["location"]]
    
    print("\n--- Stato giocatore ---")
    print(f"Posizione: {player['location']}")
    print(f"Oro: {player['gold']}")
    print("Carico nave:")
    if player['cargo']:
        for c, q in player['cargo'].items():
            print(f"  {c}: {q}")
    else:
        print("  Vuoto")
    
    print("\n--- Merci disponibili in città ---")
    for commodity, qty in city["inventory"].items():
        price = calculate_price(city, commodity)
        print(f"  {commodity}: {qty} unità, prezzo {price} oro/unità")
    print("----------------------\n")
    
def consume_resources():
    for city_name, city in cities.items():
        for commodity, demand in city["demand"].items():
            if commodity in city["inventory"]:
                stock = city["inventory"][commodity]
                consumption = int(demand * 0.1)  # Consuma il 10% della domanda
                consumption = min(consumption, stock)  # Non può consumare più dello stock
                city["inventory"][commodity] -= consumption
                print(f"{city_name} ha consumato {consumption} unità di {commodity}.")
                
#-----------------------------------------------------------------

events_catalog = {
    "carestia": {
        "description": "La città soffre una grave carestia, la domanda di cibo aumenta e la produzione cala.",
        "effects": {
            "demand_multiplier": {"grano": 2, "olio": 1.5, "pesce": 2},
            "production_multiplier": 0.5,
        },
        "duration": 5,
        "probability": 0.05  # 5% a ogni loop
    },
    "guerra": {
        "description": "Conflitto in città, produzione e domanda diminuiscono, prezzi volatili.",
        "effects": {
            "demand_multiplier": 0.7,
            "production_multiplier": 0.6,
            "price_volatility": 0.3,
        },
        "duration": 7,
        "probability": 0.03
    },
    "epidemia": {
        "description": "Un'epidemia riduce la popolazione, la domanda scende ma la produzione è rallentata.",
        "effects": {
            "demand_multiplier": 0.5,
            "production_multiplier": 0.7,
        },
        "duration": 6,
        "probability": 0.05
    }
}

# Attivi eventi per città
active_events = {city: [] for city in cities}

def check_new_events():
    for city in cities:
        for event_name, event in events_catalog.items():
            if random.random() < event["probability"]:
                print(f"Evento {event_name.upper()} in {city}! {event['description']}")
                active_events[city].append({"name": event_name, "turns_left": event["duration"]})

def apply_event_effects(city_name):
    city = cities[city_name]
    events = active_events[city_name]
    
    # Moltiplicatori di domanda e produzione
    demand_mult = 1.0
    prod_mult = 1.0
    price_volatility = 0.0
    
    for event in events:
        e = events_catalog[event["name"]]
        eff = e["effects"]
        
        # Demand multiplier può essere singolo float o dict per commodity
        dm = eff.get("demand_multiplier", 1.0)
        if isinstance(dm, dict):
            for c, m in dm.items():
                city["demand"][c] = int(city["demand"].get(c, 0) * m)
        else:
            demand_mult *= dm
        
        prod_mult *= eff.get("production_multiplier", 1.0)
        price_volatility += eff.get("price_volatility", 0.0)
    
    # Applica moltiplicatori globali (per domanda)
    if demand_mult != 1.0:
        for c in city["demand"]:
            city["demand"][c] = int(city["demand"][c] * demand_mult)
    
    return prod_mult, price_volatility

def decrement_event_timers():
    for city, events in active_events.items():
        for event in events[:]:
            event["turns_left"] -= 1
            if event["turns_left"] <= 0:
                print(f"L'evento {event['name']} a {city} è terminato.")
                events.remove(event)

#------------------------------------------------------------------------------------------------------------------------------------
import tkinter as tk
from tkinter import simpledialog, messagebox

# --------------------
# FUNZIONI DI INTERFACCIA
# --------------------

turn_number = 1

def update_status(extra_msg=""):
    """Aggiorna la Label dello status e la lista eventi"""
    city = cities[player["location"]]

    status_lines = []
    status_lines.append(f"Turno: {turn_number}")  # Mostra il numero del turno
    status_lines.append(f"Posizione: {player['location']}")
    status_lines.append(f"Oro: {player['gold']}")
    status_lines.append("Carico nave:")

    if player['cargo']:
        for c, (q, avg_price) in player['cargo'].items():
            status_lines.append(f"  {c}: {q} unità (Prezzo medio acquisto: {avg_price:.2f})")
    else:
        status_lines.append("  Vuoto")

    status_lines.append("\nMerci disponibili in città:")
    for commodity, qty in city["inventory"].items():
        buy_price, sell_price = calculate_price(city, commodity)
        status_lines.append(f"  {commodity}: {qty} unità | Prezzo acquisto: {buy_price} | Prezzo vendita: {sell_price}")

    if extra_msg:
        status_lines.append("\n" + extra_msg)

    status_text.set("\n".join(status_lines))

    # Aggiorna events_box
    events_box.delete(0, tk.END)
    for city_name, events in active_events.items():
        for e in events:
            events_box.insert(tk.END, f"{city_name}: {e['name']} ({e['turns_left']} turni rimanenti)")


# --------------------
# Funzioni azioni aggiornate
# --------------------

def buy_action():
    city_name = player["location"]
    city = cities[city_name]

    buy_win = tk.Toplevel(root)
    buy_win.title("Compra merci")
    tk.Label(buy_win, text="Seleziona la merce da comprare:").pack(pady=5)

    def calculate_average_buy_price(city, commodity, qty):
        total_cost = 0
        stock = city["inventory"].get(commodity, 0)
        demand = city["demand"].get(commodity, 0)
    
        for i in range(qty):
            current_stock = stock - i
            modifier = 1 + (demand - current_stock) / 100
            unit_price = max(1, int(commodities[commodity]["base_price"] * modifier))
    
            cap = price_caps.get(commodity)
            if cap is not None:
                unit_price = min(unit_price, cap)
    
            # spread tra buy e sell
            unit_price *= (1+spread) # +X% per acquisto
            total_cost += unit_price
    
        if qty > 0:
            return total_cost / qty, total_cost
        else:
            return 0, 0


    def select_commodity(commodity):
        for widget in buy_win.winfo_children():
            widget.destroy()

        available_qty = city["inventory"].get(commodity, 0)
        current_qty, current_avg = player["cargo"].get(commodity, (0, 0.0))
        tk.Label(buy_win, text=f"{commodity} - Disponibili in città: {available_qty}").pack()
        tk.Label(buy_win, text=f"Oro disponibile: {player['gold']}").pack()

        amount_var = tk.IntVar(value=1)
        slider = tk.Scale(buy_win, from_=1, to=available_qty, orient=tk.HORIZONTAL, variable=amount_var)
        slider.pack()

        # Label dinamica
        price_label = tk.Label(buy_win, text="")
        price_label.pack()

        def update_price_label(*args):
            qty_to_buy = amount_var.get()
            avg_unit_price, total_cost = calculate_average_buy_price(city, commodity, qty_to_buy)

            # Nuovo prezzo medio nel cargo
            if current_qty + qty_to_buy > 0:
                new_avg = (current_avg * current_qty + total_cost) / (current_qty + qty_to_buy)
            else:
                new_avg = avg_unit_price

            price_label.config(
                text=f"Prezzo medio unitario (progressivo): {avg_unit_price:.2f} | "
                     f"Nuovo prezzo medio in stiva: {new_avg:.2f} | "
                     f"Costo totale: {total_cost} oro"
            )

        amount_var.trace("w", update_price_label)
        update_price_label()

        def confirm_purchase():
            qty_to_buy = amount_var.get()
            avg_unit_price, total_cost = calculate_average_buy_price(city, commodity, qty_to_buy)

            if player["gold"] < total_cost:
                messagebox.showinfo("Errore", "Oro insufficiente!")
                return
            if sum(q for q, _ in player["cargo"].values()) + qty_to_buy > player["capacity"]:
                messagebox.showinfo("Errore", "Capacità nave insufficiente!")
                return

            # Aggiorna cargo e oro
            new_qty = current_qty + qty_to_buy
            new_avg = (current_avg * current_qty + total_cost) / new_qty
            player["cargo"][commodity] = (new_qty, new_avg)
            player["gold"] -= total_cost

            # Aggiorna stock e domanda della città
            city["inventory"][commodity] -= qty_to_buy
            city["demand"][commodity] = city["demand"].get(commodity, 0) + qty_to_buy

            update_status()
            messagebox.showinfo(
                "Compra",
                f"✅ Comprato {qty_to_buy} di {commodity} per {total_cost} oro (prezzo medio {avg_unit_price:.2f})"
            )
            buy_win.destroy()

        tk.Button(buy_win, text="Conferma acquisto", command=confirm_purchase).pack()

    # Bottoni per ogni merce disponibile
    for commodity, qty in city["inventory"].items():
        if qty > 0:
            tk.Button(
                buy_win,
                text=f"{commodity} ({qty} disponibili)",
                command=lambda c=commodity: select_commodity(c)
            ).pack(pady=2)


def sell_action():
    city_name = player["location"]
    city = cities[city_name]

    sell_win = tk.Toplevel(root)
    sell_win.title("Vendi merci")
    tk.Label(sell_win, text="Seleziona la merce da vendere:").pack(pady=5)

    def calculate_average_sell_price(city, commodity, qty):
        total_revenue = 0
        stock = city["inventory"].get(commodity, 0)
        demand = city["demand"].get(commodity, 0)
    
        for i in range(qty):
            current_stock = stock + i
            modifier = 1 + (demand - current_stock) / 100
            unit_price = max(1, int(commodities[commodity]["base_price"] * modifier))
    
            cap = price_caps.get(commodity)
            if cap is not None:
                unit_price = min(unit_price, cap)
    
            # spread tra buy e sell
            unit_price *= (1-spread)  # -X% per vendita
            total_revenue += unit_price
    
        if qty > 0:
            return total_revenue / qty, total_revenue
        else:
            return 0, 0


    def select_commodity(commodity):
        for widget in sell_win.winfo_children():
            widget.destroy()

        current_qty, current_avg = player["cargo"].get(commodity, (0, 0))
        tk.Label(sell_win, text=f"{commodity} - Disponibili nella nave: {current_qty}").pack()
        tk.Label(sell_win, text=f"Oro disponibile: {player['gold']}").pack()

        amount_var = tk.IntVar(value=1)
        slider = tk.Scale(sell_win, from_=1, to=current_qty, orient=tk.HORIZONTAL, variable=amount_var)
        slider.pack()

        # Label dinamica
        price_label = tk.Label(sell_win, text="")
        price_label.pack()

        def update_price_label(*args):
            qty_to_sell = amount_var.get()
            avg_unit_price, total_revenue = calculate_average_sell_price(city, commodity, qty_to_sell)

            net_revenue = int(total_revenue * (1 - fee_rate))

            price_label.config(
                text=f"Prezzo medio unitario: {avg_unit_price:.2f} | Totale lordo: {total_revenue} oro | Totale netto (5% fee): {net_revenue} oro"
            )

        amount_var.trace("w", update_price_label)
        update_price_label()

        def confirm_sale():
            qty_to_sell = amount_var.get()
            avg_unit_price, total_revenue = calculate_average_sell_price(city, commodity, qty_to_sell)

            net_revenue = int(total_revenue * (1 - fee_rate))

            if player["cargo"].get(commodity, (0, 0))[0] < qty_to_sell:
                messagebox.showinfo("Errore", "Non hai abbastanza merce da vendere!")
                return

            # Aggiorna cargo e oro
            current_qty, current_avg = player["cargo"].get(commodity, (0, 0))
            new_qty = current_qty - qty_to_sell
            if new_qty > 0:
                player["cargo"][commodity] = (new_qty, current_avg)
            else:
                del player["cargo"][commodity]
            player["gold"] += net_revenue

            # Aggiorna città
            city["inventory"][commodity] = city["inventory"].get(commodity, 0) + qty_to_sell
            city["demand"][commodity] = max(0, city["demand"].get(commodity, 0) - qty_to_sell)

            update_status()
            messagebox.showinfo(
                "Vendi",
                f"✅ Venduto {qty_to_sell} di {commodity} per {net_revenue} oro (prezzo medio {avg_unit_price:.2f})"
            )
            sell_win.destroy()

        tk.Button(sell_win, text="Conferma vendita", command=confirm_sale).pack()

    # Bottoni per ogni merce disponibile nella nave
    for commodity, (qty, avg) in player["cargo"].items():
        if qty > 0:
            tk.Button(sell_win, text=f"{commodity} ({qty} in stiva)", command=lambda c=commodity: select_commodity(c)).pack(pady=2)


def travel_action():
    if player["in_viaggio"]:
        messagebox.showinfo("Viaggio", "Sei già in viaggio!")
        return

    travel_win = tk.Toplevel(root)
    travel_win.title("Viaggia")

    tk.Label(travel_win, text="Seleziona la città di destinazione:").pack(pady=5)

    current = player["location"]

    # Creiamo bottoni solo per le città raggiungibili dalla città attuale
    for (from_city, to_city), days in travel_times.items():
        if from_city == current:
            def make_travel(dest=to_city, durata=days):
                def start_travel():
                    player["in_viaggio"] = True
                    player["destinazione"] = dest
                    player["giorni_rimanenti"] = durata
                    messagebox.showinfo("Viaggio", f"Partito da {current} verso {dest}. Arrivo in {durata} turni!")
                    travel_win.destroy()
                    update_status()
                return start_travel
            tk.Button(travel_win, text=f"{to_city} ({days} giorni)", command=make_travel()).pack(pady=2)

def wait_action():
    if player["in_viaggio"]:
        messagebox.showinfo("Aspetta", "Sei in viaggio, non puoi aspettare a terra!")
        return
    
    game_turn()
    messagebox.showinfo("Turno passato", "Hai aspettato un turno.")

# --------------------
# LOOP DI GIOCO
# --------------------



def game_turn():
    global turn_number
    turn_number += 1  # Incrementa il turno

    # Controlla nuovi eventi
    check_new_events()

    # Applica effetti eventi e produce risorse
    for city in cities:
        prod_mult, price_vol = apply_event_effects(city)
        produce(city, production_multiplier=prod_mult)

    # Gestione viaggio
    travel_msg = ""
    if player["in_viaggio"]:
        player["giorni_rimanenti"] -= 1
        travel_msg = f"🚢 In viaggio verso {player['destinazione']}... Giorni rimanenti: {player['giorni_rimanenti']}"
        if player["giorni_rimanenti"] <= 0:
            player["location"] = player["destinazione"]
            player["in_viaggio"] = False
            player["destinazione"] = None
            travel_msg = f"✅ Sei arrivato a {player['location']}!"
    
    # Aggiorna mercato, domanda e consumi
    update_market()
    consume_resources()
    update_demand()
    decrement_event_timers()

    # Aggiorna status con eventuale messaggio di viaggio
    update_status(extra_msg=travel_msg)

    # Pagamento equipaggio
    player["gold"] -= 2
    if player["gold"] < 0:
        events_box.insert(tk.END, "💀 Hai finito l'oro e i marinai si sono ammutinati! Game Over.")
        return  # Termina loop di gioco

    # Richiama il turno successivo dopo il delay
    delay = 2000 if player["in_viaggio"] else 10000
    root.after(delay, game_turn)

def log_message(msg):
    """Mostra messaggi nel riquadro eventi"""
    events_box.insert(tk.END, msg)
    events_box.see(tk.END)


# --------------------
# INTERFACCIA GRAFICA
# --------------------

root = tk.Tk()
root.title("Mercante del Mediterraneo")

status_text = tk.StringVar()
status_label = tk.Label(root, textvariable=status_text, justify="left", font=("Arial", 12))
status_label.pack(pady=10)

goods_list = tk.Listbox(root, width=50, height=10)
goods_list.pack(pady=10)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Compra", command=buy_action).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Vendi", command=sell_action).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Viaggia", command=travel_action).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Aspetta", command=wait_action).grid(row=0, column=3, padx=5)

events_box = tk.Listbox(root, width=60, height=10)
events_box.pack(pady=10)

# Avvia
update_status()
root.after(1000, game_turn)  # Avvia il loop fra 3 secondi
root.mainloop()
