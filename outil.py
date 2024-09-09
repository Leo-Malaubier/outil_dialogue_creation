import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DialogueEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Éditeur de Quêtes et Dialogues")
        self.root.geometry("1200x800")

        # Conteneur pour stocker les dialogues, réponses, et quêtes
        self.dialogues = {}
        self.quests = {}
        self.graph = nx.DiGraph()  # Graphe orienté pour représenter les dialogues

        # Créer le menu pour gérer les NPCs
        self.create_npc_menu()

        # Cadre principal avec des onglets
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.tabs = tk.Frame(self.main_frame)
        self.tabs.pack(side=tk.LEFT, fill=tk.Y)

        self.content = tk.Frame(self.main_frame)
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Boutons d'onglet
        self.dialogues_tab = tk.Button(self.tabs, text="Dialogues", command=self.show_dialogues_tab, width=15)
        self.dialogues_tab.pack(pady=10)

        self.responses_tab = tk.Button(self.tabs, text="Réponses", command=self.show_responses_tab, width=15)
        self.responses_tab.pack(pady=10)

        self.quests_tab = tk.Button(self.tabs, text="Quêtes", command=self.show_quests_tab, width=15)
        self.quests_tab.pack(pady=10)

        self.graph_tab = tk.Button(self.tabs, text="Graphique", command=self.show_graph_tab, width=15)
        self.graph_tab.pack(pady=10)

        # Initialiser l'onglet Dialogues
        self.show_dialogues_tab()

        # Zone pour afficher les dialogues et quêtes
        self.display_frame = tk.Frame(root)
        self.display_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.display_area = tk.Text(self.display_frame, height=10, width=150)
        self.display_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Boutons de sauvegarde et chargement
        self.save_button = tk.Button(root, text="Sauvegarder", command=self.save_file)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.load_button = tk.Button(root, text="Charger", command=self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)

    def create_npc_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        npc_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="NPCs", menu=npc_menu)
        npc_menu.add_command(label="Ajouter NPC", command=self.add_npc)
        npc_menu.add_command(label="Changer NPC", command=self.switch_npc)
        npc_menu.add_command(label="Supprimer NPC", command=self.delete_npc)

        self.current_npc = None

    def add_npc(self):
        npc_name = simpledialog.askstring("Ajouter NPC", "Entrez le nom du NPC:")
        if npc_name:
            if npc_name in self.dialogues:
                messagebox.showwarning("Attention", f"Le NPC '{npc_name}' existe déjà.")
            else:
                self.dialogues[npc_name] = {'quests': {}, 'responses': {}, 'Dialogue': {}}
                self.current_npc = npc_name
                messagebox.showinfo("Succès", f"NPC '{npc_name}' ajouté.")
        else:
            messagebox.showwarning("Attention", "Le nom du NPC ne peut pas être vide.")

    def switch_npc(self):
        if not self.dialogues:
            messagebox.showwarning("Attention", "Aucun NPC disponible.")
            return
        npc_list = list(self.dialogues.keys())
        npc_name = simpledialog.askstring("Changer NPC", "Entrez le nom du NPC:", initialvalue=npc_list[0])
        if npc_name in self.dialogues:
            self.current_npc = npc_name
            messagebox.showinfo("Succès", f"Vous avez changé pour le NPC '{npc_name}'.")
            self.refresh_dialogue_list()
            self.refresh_response_list()
        else:
            messagebox.showwarning("Attention", f"Le NPC '{npc_name}' n'existe pas.")

    def delete_npc(self):
        if not self.dialogues:
            messagebox.showwarning("Attention", "Aucun NPC à supprimer.")
            return
        npc_name = simpledialog.askstring("Supprimer NPC", "Entrez le nom du NPC à supprimer:")
        if npc_name:
            if npc_name in self.dialogues:
                del self.dialogues[npc_name]
                messagebox.showinfo("Succès", f"NPC '{npc_name}' supprimé.")
                if self.current_npc == npc_name:
                    self.current_npc = None
                self.update_graph()
                self.refresh_display()
            else:
                messagebox.showwarning("Attention", f"Le NPC '{npc_name}' n'existe pas.")
        else:
            messagebox.showwarning("Attention", "Le nom du NPC ne peut pas être vide.")

    def show_dialogues_tab(self):
        self.clear_content()
        if not self.current_npc:
            messagebox.showwarning("Attention", "Veuillez sélectionner un NPC ou en ajouter un.")
            return
        # Cadre pour ajouter/modifier/supprimer des dialogues
        dialogue_control_frame = tk.Frame(self.content)
        dialogue_control_frame.pack(pady=10)

        tk.Label(dialogue_control_frame, text="Dialogue:").grid(row=0, column=0, padx=5, pady=5)
        self.dialogue_entry = tk.Entry(dialogue_control_frame, width=50)
        self.dialogue_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialogue_control_frame, text="Déclencher Quête (ID):").grid(row=0, column=2, padx=5, pady=5)
        self.quest_entry = tk.Entry(dialogue_control_frame, width=10)
        self.quest_entry.grid(row=0, column=3, padx=5, pady=5)

        add_dialogue_btn = tk.Button(dialogue_control_frame, text="Ajouter Dialogue", command=self.add_dialogue)
        add_dialogue_btn.grid(row=0, column=4, padx=5, pady=5)

        edit_dialogue_btn = tk.Button(dialogue_control_frame, text="Modifier Dialogue", command=self.edit_dialogue)
        edit_dialogue_btn.grid(row=0, column=5, padx=5, pady=5)

        delete_dialogue_btn = tk.Button(dialogue_control_frame, text="Supprimer Dialogue", command=self.delete_dialogue)
        delete_dialogue_btn.grid(row=0, column=6, padx=5, pady=5)

        # Liste des dialogues
        self.dialogue_listbox = tk.Listbox(self.content, width=100)
        self.dialogue_listbox.pack(pady=10)
        self.dialogue_listbox.bind('<<ListboxSelect>>', self.on_dialogue_select)
        self.refresh_dialogue_list()

    def show_responses_tab(self):
        self.clear_content()
        if not self.current_npc:
            messagebox.showwarning("Attention", "Veuillez sélectionner un NPC ou en ajouter un.")
            return
        # Cadre pour ajouter/modifier/supprimer des réponses
        response_control_frame = tk.Frame(self.content)
        response_control_frame.pack(pady=10)

        tk.Label(response_control_frame, text="Réponse:").grid(row=0, column=0, padx=5, pady=5)
        self.response_entry = tk.Entry(response_control_frame, width=50)
        self.response_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(response_control_frame, text="Dialogue Suivant (ID):").grid(row=0, column=2, padx=5, pady=5)
        self.next_dialogue_entry = tk.Entry(response_control_frame, width=10)
        self.next_dialogue_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(response_control_frame, text="Dialogue Précédent (ID):").grid(row=0, column=4, padx=5, pady=5)
        self.prev_dialogue_entry = tk.Entry(response_control_frame, width=10)  # Champ pour spécifier le dialogue précédent
        self.prev_dialogue_entry.grid(row=0, column=5, padx=5, pady=5)

        tk.Label(response_control_frame, text="Déclencher Quête (ID):").grid(row=0, column=6, padx=5, pady=5)
        self.response_quest_entry = tk.Entry(response_control_frame, width=10)
        self.response_quest_entry.grid(row=0, column=7, padx=5, pady=5)

        add_response_btn = tk.Button(response_control_frame, text="Ajouter Réponse", command=self.add_response)
        add_response_btn.grid(row=0, column=8, padx=5, pady=5)

        edit_response_btn = tk.Button(response_control_frame, text="Modifier Réponse", command=self.edit_response)
        edit_response_btn.grid(row=0, column=9, padx=5, pady=5)

        delete_response_btn = tk.Button(response_control_frame, text="Supprimer Réponse", command=self.delete_response)
        delete_response_btn.grid(row=0, column=10, padx=5, pady=5)

        # Liste des réponses
        self.response_listbox = tk.Listbox(self.content, width=100)
        self.response_listbox.pack(pady=10)
        self.response_listbox.bind('<<ListboxSelect>>', self.on_response_select)
        self.refresh_response_list()

    def show_quests_tab(self):
        self.clear_content()
        # Cadre pour ajouter/modifier/supprimer des quêtes
        quest_control_frame = tk.Frame(self.content)
        quest_control_frame.pack(pady=10)

        tk.Label(quest_control_frame, text="ID Quête:").grid(row=0, column=0, padx=5, pady=5)
        self.quest_id_entry = tk.Entry(quest_control_frame, width=10)
        self.quest_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(quest_control_frame, text="Description:").grid(row=0, column=2, padx=5, pady=5)
        self.quest_desc_entry = tk.Entry(quest_control_frame, width=50)
        self.quest_desc_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(quest_control_frame, text="Récompense:").grid(row=0, column=4, padx=5, pady=5)
        self.quest_reward_entry = tk.Entry(quest_control_frame, width=20)
        self.quest_reward_entry.grid(row=0, column=5, padx=5, pady=5)

        add_quest_btn = tk.Button(quest_control_frame, text="Ajouter Quête", command=self.add_quest)
        add_quest_btn.grid(row=0, column=6, padx=5, pady=5)

        edit_quest_btn = tk.Button(quest_control_frame, text="Modifier Quête", command=self.edit_quest)
        edit_quest_btn.grid(row=0, column=7, padx=5, pady=5)

        delete_quest_btn = tk.Button(quest_control_frame, text="Supprimer Quête", command=self.delete_quest)
        delete_quest_btn.grid(row=0, column=8, padx=5, pady=5)

        # Liste des quêtes
        self.quest_listbox = tk.Listbox(self.content, width=100)
        self.quest_listbox.pack(pady=10)
        self.quest_listbox.bind('<<ListboxSelect>>', self.on_quest_select)
        self.refresh_quest_list()

    def show_graph_tab(self):
        self.clear_content()
        # Zone pour afficher le graphe
        self.graph_frame = tk.Frame(self.content)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.update_graph()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def add_dialogue(self):
        dialogue = self.dialogue_entry.get().strip()
        quest_id = self.quest_entry.get().strip()
        if not dialogue:
            messagebox.showwarning("Attention", "Veuillez entrer un dialogue.")
            return
        if quest_id and quest_id not in self.quests:
            messagebox.showwarning("Attention", f"La quête ID '{quest_id}' n'existe pas.")
            return
        npc = self.current_npc
        dialogue_id = len(self.dialogues[npc]['Dialogue']) + 1
        quest_trigger = int(quest_id) if quest_id else 0
        self.dialogues[npc]['Dialogue'][str(dialogue_id)] = {"text": dialogue, "quest_trigger": quest_trigger, "responses": []}
        self.display_area.insert(tk.END, f"Ajouté dialogue {dialogue_id}: {dialogue} (Déclenche Quête: {quest_trigger})\n")
        self.refresh_dialogue_list()
        self.update_graph()
        self.dialogue_entry.delete(0, tk.END)
        self.quest_entry.delete(0, tk.END)

    def edit_dialogue(self):
        selected = self.dialogue_listbox.curselection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dialogue à modifier.")
            return
        index = selected[0]
        npc = self.current_npc
        dialogue_id = list(self.dialogues[npc]['Dialogue'].keys())[index]
        current_dialogue = self.dialogues[npc]['Dialogue'][dialogue_id]["text"]
        current_quest = self.dialogues[npc]['Dialogue'][dialogue_id]["quest_trigger"]

        new_dialogue = simpledialog.askstring("Modifier Dialogue", "Entrez le nouveau texte du dialogue:", initialvalue=current_dialogue)
        if new_dialogue is None:
            return  # Annulé
        new_dialogue = new_dialogue.strip()
        if not new_dialogue:
            messagebox.showwarning("Attention", "Le texte du dialogue ne peut pas être vide.")
            return

        new_quest_id = simpledialog.askstring("Modifier Quête", "Entrez le nouvel ID de quête (laisser vide si aucune):", initialvalue=str(current_quest) if current_quest else "")
        if new_quest_id:
            if new_quest_id not in self.quests:
                messagebox.showwarning("Attention", f"La quête ID '{new_quest_id}' n'existe pas.")
                return
            new_quest_id = int(new_quest_id)
        else:
            new_quest_id = 0

        self.dialogues[npc]['Dialogue'][dialogue_id]["text"] = new_dialogue
        self.dialogues[npc]['Dialogue'][dialogue_id]["quest_trigger"] = new_quest_id
        self.display_area.insert(tk.END, f"Modifié dialogue {dialogue_id}: {new_dialogue} (Déclenche Quête: {new_quest_id})\n")
        self.refresh_dialogue_list()
        self.update_graph()

    def delete_dialogue(self):
        selected = self.dialogue_listbox.curselection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dialogue à supprimer.")
            return
        index = selected[0]
        npc = self.current_npc
        dialogue_id = list(self.dialogues[npc]['Dialogue'].keys())[index]
        confirm = messagebox.askyesno("Confirmer", f"Êtes-vous sûr de vouloir supprimer le dialogue {dialogue_id}?")
        if confirm:
            del self.dialogues[npc]['Dialogue'][dialogue_id]
            self.display_area.insert(tk.END, f"Supprimé dialogue {dialogue_id}\n")
            self.refresh_dialogue_list()
            self.update_graph()

    def on_dialogue_select(self, event):
        selected = self.dialogue_listbox.curselection()
        if selected:
            index = selected[0]
            npc = self.current_npc
            dialogue_id = list(self.dialogues[npc]['Dialogue'].keys())[index]
            dialogue = self.dialogues[npc]['Dialogue'][dialogue_id]["text"]
            quest = self.dialogues[npc]['Dialogue'][dialogue_id]["quest_trigger"]
            self.display_area.insert(tk.END, f"Sélectionné Dialogue {dialogue_id}: {dialogue} (Quête: {quest})\n")

    def refresh_dialogue_list(self):
        self.dialogue_listbox.delete(0, tk.END)
        npc = self.current_npc
        for dialogue_id, dialogue in self.dialogues[npc]['Dialogue'].items():
            quest_info = f" (Quête ID: {dialogue['quest_trigger']})" if dialogue['quest_trigger'] else ""
            self.dialogue_listbox.insert(tk.END, f"ID {dialogue_id}: {dialogue['text']}{quest_info}")

    def add_response(self):
        response = self.response_entry.get().strip()
        next_dialogue = self.next_dialogue_entry.get().strip()
        prev_dialogue = self.prev_dialogue_entry.get().strip()  # Nouveau champ pour dialogue précédent
        quest_id = self.response_quest_entry.get().strip()
        if not response:
            messagebox.showwarning("Attention", "Veuillez entrer une réponse.")
            return
        if next_dialogue and next_dialogue not in self.dialogues[self.current_npc]['Dialogue']:
            messagebox.showwarning("Attention", f"Le dialogue suivant ID '{next_dialogue}' n'existe pas.")
            return
        if prev_dialogue and prev_dialogue not in self.dialogues[self.current_npc]['Dialogue']:
            messagebox.showwarning("Attention", f"Le dialogue précédent ID '{prev_dialogue}' n'existe pas.")
            return
        if quest_id and quest_id not in self.quests:
            messagebox.showwarning("Attention", f"La quête ID '{quest_id}' n'existe pas.")
            return
        npc = self.current_npc
        response_id = len(self.dialogues[npc]['responses']) + 1
        next_dialogue_id = int(next_dialogue) if next_dialogue else None
        prev_dialogue_id = int(prev_dialogue) if prev_dialogue else None
        quest_trigger = int(quest_id) if quest_id else 0
        self.dialogues[npc]['responses'][str(response_id)] = {"text": response, "next_dialogue": next_dialogue_id, "prev_dialogue": prev_dialogue_id, "quest_trigger": quest_trigger}
        self.display_area.insert(tk.END, f"Ajouté réponse {response_id}: {response} (Dialogue suivant: {next_dialogue if next_dialogue else 'N/A'}) (Dialogue précédent: {prev_dialogue if prev_dialogue else 'N/A'}) (Quête: {quest_trigger})\n")
        self.refresh_response_list()
        self.update_graph()
        self.response_entry.delete(0, tk.END)
        self.next_dialogue_entry.delete(0, tk.END)
        self.prev_dialogue_entry.delete(0, tk.END)
        self.response_quest_entry.delete(0, tk.END)

    def edit_response(self):
        selected = self.response_listbox.curselection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une réponse à modifier.")
            return
        index = selected[0]
        npc = self.current_npc
        response_id = list(self.dialogues[npc]['responses'].keys())[index]
        current_response = self.dialogues[npc]['responses'][response_id]["text"]
        current_next = self.dialogues[npc]['responses'][response_id]["next_dialogue"]
        current_prev = self.dialogues[npc]['responses'][response_id]["prev_dialogue"]
        current_quest = self.dialogues[npc]['responses'][response_id]["quest_trigger"]

        new_response = simpledialog.askstring("Modifier Réponse", "Entrez le nouveau texte de la réponse:", initialvalue=current_response)
        if new_response is None:
            return  # Annulé
        new_response = new_response.strip()
        if not new_response:
            messagebox.showwarning("Attention", "Le texte de la réponse ne peut pas être vide.")
            return

        new_next = simpledialog.askstring("Modifier Dialogue Suivant", "Entrez le nouvel ID du dialogue suivant (laisser vide si aucun):", initialvalue=str(current_next) if current_next else "")
        if new_next:
            if new_next not in self.dialogues[npc]['Dialogue']:
                messagebox.showwarning("Attention", f"Le dialogue suivant ID '{new_next}' n'existe pas.")
                return
            new_next = int(new_next)
        else:
            new_next = None

        new_prev = simpledialog.askstring("Modifier Dialogue Précédent", "Entrez le nouvel ID du dialogue précédent (laisser vide si aucun):", initialvalue=str(current_prev) if current_prev else "")
        if new_prev:
            if new_prev not in self.dialogues[npc]['Dialogue']:
                messagebox.showwarning("Attention", f"Le dialogue précédent ID '{new_prev}' n'existe pas.")
                return
            new_prev = int(new_prev)
        else:
            new_prev = None

        new_quest = simpledialog.askstring("Modifier Quête", "Entrez le nouvel ID de quête (laisser vide si aucune):", initialvalue=str(current_quest) if current_quest else "")
        if new_quest:
            if new_quest not in self.quests:
                messagebox.showwarning("Attention", f"La quête ID '{new_quest}' n'existe pas.")
                return
            new_quest = int(new_quest)
        else:
            new_quest = 0

        self.dialogues[npc]['responses'][response_id]["text"] = new_response
        self.dialogues[npc]['responses'][response_id]["next_dialogue"] = new_next
        self.dialogues[npc]['responses'][response_id]["prev_dialogue"] = new_prev
        self.dialogues[npc]['responses'][response_id]["quest_trigger"] = new_quest
        self.display_area.insert(tk.END, f"Modifié réponse {response_id}: {new_response} (Dialogue suivant: {new_next if new_next else 'N/A'}) (Dialogue précédent: {new_prev if new_prev else 'N/A'}) (Quête: {new_quest})\n")
        self.refresh_response_list()
        self.update_graph()

    def delete_response(self):
        selected = self.response_listbox.curselection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une réponse à supprimer.")
            return
        index = selected[0]
        npc = self.current_npc
        response_id = list(self.dialogues[npc]['responses'].keys())[index]
        confirm = messagebox.askyesno("Confirmer", f"Êtes-vous sûr de vouloir supprimer la réponse {response_id}?")
        if confirm:
            del self.dialogues[npc]['responses'][response_id]
            self.display_area.insert(tk.END, f"Supprimé réponse {response_id}\n")
            self.refresh_response_list()
            self.update_graph()

    def on_response_select(self, event):
        selected = self.response_listbox.curselection()
        if selected:
            index = selected[0]
            npc = self.current_npc
            response_id = list(self.dialogues[npc]['responses'].keys())[index]
            response = self.dialogues[npc]['responses'][response_id]["text"]
            next_dialogue = self.dialogues[npc]['responses'][response_id]["next_dialogue"]
            prev_dialogue = self.dialogues[npc]['responses'][response_id]["prev_dialogue"]
            quest = self.dialogues[npc]['responses'][response_id]["quest_trigger"]
            self.display_area.insert(tk.END, f"Sélectionné Réponse {response_id}: {response} (Dialogue suivant: {next_dialogue if next_dialogue else 'N/A'}) (Dialogue précédent: {prev_dialogue if prev_dialogue else 'N/A'}) (Quête: {quest})\n")

    def refresh_response_list(self):
        self.response_listbox.delete(0, tk.END)
        npc = self.current_npc
        for response_id, response in self.dialogues[npc]['responses'].items():
            next_info = f" (Dialogue suivant: {response['next_dialogue']})" if response['next_dialogue'] else ""
            prev_info = f" (Dialogue précédent: {response['prev_dialogue']})" if response['prev_dialogue'] else ""
            quest_info = f" (Quête ID: {response['quest_trigger']})" if response['quest_trigger'] else ""
            self.response_listbox.insert(tk.END, f"ID {response_id}: {response['text']}{next_info}{prev_info}{quest_info}")

    def add_quest(self):
        quest_id = self.quest_id_entry.get().strip()
        description = self.quest_desc_entry.get().strip()
        reward = self.quest_reward_entry.get().strip()
        if not quest_id or not description or not reward:
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs de la quête.")
            return
        if quest_id in self.quests:
            messagebox.showwarning("Attention", f"La quête ID '{quest_id}' existe déjà.")
            return
        self.quests[quest_id] = {"description": description, "reward": reward}
        self.display_area.insert(tk.END, f"Ajouté quête {quest_id}: {description} (Récompense: {reward})\n")
        self.refresh_quest_list()
        self.quest_id_entry.delete(0, tk.END)
        self.quest_desc_entry.delete(0, tk.END)
        self.quest_reward_entry.delete(0, tk.END)

    def edit_quest(self):
        selected = self.quest_listbox.curselection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une quête à modifier.")
            return
        index = selected[0]
        quest_id = list(self.quests.keys())[index]
        current_desc = self.quests[quest_id]["description"]
        current_reward = self.quests[quest_id]["reward"]

        new_desc = simpledialog.askstring("Modifier Quête", "Entrez la nouvelle description de la quête:", initialvalue=current_desc)
        if new_desc is None:
            return  # Annulé
        new_desc = new_desc.strip()
        if not new_desc:
            messagebox.showwarning("Attention", "La description de la quête ne peut pas être vide.")
            return

        new_reward = simpledialog.askstring("Modifier Récompense", "Entrez la nouvelle récompense de la quête:", initialvalue=current_reward)
        if new_reward is None:
            return  # Annulé
        new_reward = new_reward.strip()
        if not new_reward:
            messagebox.showwarning("Attention", "La récompense de la quête ne peut pas être vide.")
            return

        self.quests[quest_id]["description"] = new_desc
        self.quests[quest_id]["reward"] = new_reward
        self.display_area.insert(tk.END, f"Modifié quête {quest_id}: {new_desc} (Récompense: {new_reward})\n")
        self.refresh_quest_list()
        self.update_graph()

    def delete_quest(self):
        selected = self.quest_listbox.curselection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une quête à supprimer.")
            return
        index = selected[0]
        quest_id = list(self.quests.keys())[index]
        confirm = messagebox.askyesno("Confirmer", f"Êtes-vous sûr de vouloir supprimer la quête {quest_id}?")
        if confirm:
            del self.quests[quest_id]
            self.display_area.insert(tk.END, f"Supprimé quête {quest_id}\n")
            # Mettre à jour les dialogues et réponses qui déclenchent cette quête
            for npc, data in self.dialogues.items():
                for dialogue_id, dialogue in data['Dialogue'].items():
                    if dialogue["quest_trigger"] == int(quest_id):
                        self.dialogues[npc]['Dialogue'][dialogue_id]["quest_trigger"] = 0
                for response_id, response in data['responses'].items():
                    if response["quest_trigger"] == int(quest_id):
                        self.dialogues[npc]['responses'][response_id]["quest_trigger"] = 0
            self.refresh_quest_list()
            self.update_graph()

    def on_quest_select(self, event):
        selected = self.quest_listbox.curselection()
        if selected:
            index = selected[0]
            quest_id = list(self.quests.keys())[index]
            quest = self.quests[quest_id]
            self.display_area.insert(tk.END, f"Sélectionné Quête {quest_id}: {quest['description']} (Récompense: {quest['reward']})\n")

    def refresh_quest_list(self):
        self.quest_listbox.delete(0, tk.END)
        for quest_id, quest in self.quests.items():
            self.quest_listbox.insert(tk.END, f"ID {quest_id}: {quest['description']} (Récompense: {quest['reward']})")

    def update_graph(self):
        self.graph.clear()
        # Ajout des dialogues et réponses pour chaque NPC
        for npc, data in self.dialogues.items():
            for dialogue_id, dialogue in data['Dialogue'].items():
                node_label = f"NPC:{npc} D{dialogue_id}: {dialogue['text']}"
                self.graph.add_node(f"D_{npc}_{dialogue_id}", label=node_label, type='dialogue')
                if dialogue['quest_trigger']:
                    quest = self.quests.get(str(dialogue['quest_trigger']), {"description": "Inconnue", "reward": "N/A"})
                    quest_label = f"Quête {dialogue['quest_trigger']}: {quest['description']}"
                    self.graph.add_node(f"Q_{dialogue['quest_trigger']}", label=quest_label, type='quest')
                    self.graph.add_edge(f"D_{npc}_{dialogue_id}", f"Q_{dialogue['quest_trigger']}", label='Déclenche')
                for response_id in dialogue['responses']:
                    self.graph.add_edge(f"D_{npc}_{dialogue_id}", f"R_{npc}_{response_id}", label='Répond')
            for response_id, response in data['responses'].items():
                response_label = f"R{response_id}: {response['text']}"
                self.graph.add_node(f"R_{npc}_{response_id}", label=response_label, type='response')
                # Ajouter une arête vers le dialogue suivant si spécifié
                if response['next_dialogue']:
                    self.graph.add_edge(f"R_{npc}_{response_id}", f"D_{npc}_{response['next_dialogue']}", label='Suit')
                # Ajouter une arête vers le dialogue précédent si spécifié
                if response['prev_dialogue']:
                    self.graph.add_edge(f"D_{npc}_{response['prev_dialogue']}", f"R_{npc}_{response_id}", label='Précède')
                # Ajouter une arête vers une quête si la réponse déclenche une quête
                if response['quest_trigger']:
                    quest_label = f"Quête {response['quest_trigger']}: {self.quests[str(response['quest_trigger'])]['description']}"
                    self.graph.add_edge(f"R_{npc}_{response_id}", f"Q_{response['quest_trigger']}", label='Déclenche')

        self.ax.clear()
        pos = nx.spring_layout(self.graph, seed=42)
        labels = nx.get_node_attributes(self.graph, 'label')
        node_colors = []
        for node, attr in self.graph.nodes(data=True):
            if attr['type'] == 'dialogue':
                node_colors.append('skyblue')
            elif attr['type'] == 'response':
                node_colors.append('lightgreen')
            elif attr['type'] == 'quest':
                node_colors.append('salmon')
            else:
                node_colors.append('grey')

        nx.draw(self.graph, pos, ax=self.ax, with_labels=True, labels=labels,
                node_size=2000, node_color=node_colors, font_size=8, font_weight="bold", arrows=True)

        # Dessiner les étiquettes des arêtes
        edge_labels = nx.get_edge_attributes(self.graph, 'label')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=8)

        self.ax.set_title("Graphe des Dialogues, Réponses et Quêtes")
        self.ax.axis('off')
        self.canvas.draw()

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            data = {'dialogues': self.dialogues, 'quests': self.quests}
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            messagebox.showinfo("Sauvegarde", "Fichier sauvegardé avec succès !")

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.dialogues = data.get('dialogues', {})
                self.quests = data.get('quests', {})
                self.display_area.delete(1.0, tk.END)
                self.display_area.insert(tk.END, "Fichier chargé avec succès !\n")
                self.refresh_dialogue_list()
                self.refresh_response_list()
                self.refresh_quest_list()
                self.update_graph()
            messagebox.showinfo("Chargement", "Fichier chargé avec succès !")




    def refresh_display(self):
        self.display_area.delete(1.0, tk.END)
        self.display_area.insert(tk.END, "Données mises à jour.\n")

def  on_closing():
    root.destroy()
    sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = DialogueEditor(root)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
