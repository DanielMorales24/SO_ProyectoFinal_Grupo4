import tkinter as tk
from tkinter import Frame, Toplevel, messagebox, simpledialog, filedialog, ttk
import os
import shutil
import json

class FileSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proyecto Final, Sistemas Operativos - Sistema de Archivos")
        self.current_directory = os.getcwd()  # Directorio inicial (Donde esta el proyecto)
        self.allocation_table = {}  # Allocation Table FAT32
        self.journal = []  # Journal EXT
        self.mft = {}  # MFT NTFS
        self.disk_blocks = 1000  # N total de bloques(clusters) para la simulacion
        self.used_blocks = 0  # Bloques ya usados
        self.block_usage = {}  # Rellenador de archivos para simular el uso de bloques por archivo
        self.reserved_blocks = 0  # Bloques reservados para estructuras de sistema de archivos
        self.selected_algorithm = ""  # Algoritmo seleccionado por el usuario
        self.load_data()
        self.create_main_menu()

    def create_main_menu(self):
        self.clear_window()

        label = tk.Label(self.root, text="File System", font=("Arial", 16))
        label.pack(pady=20)

        btn_config_os = tk.Button(self.root, text="Configuracion OS", command=self.config_os, width=30)
        btn_config_os.pack(pady=10)

        btn_config_disk = tk.Button(self.root, text="Configuracion Disco Local", command=self.config_disk, width=30)
        btn_config_disk.pack(pady=10)

        btn_operations = tk.Button(self.root, text="Ejecucion de Operaciones con Archivos", command=self.file_operations, width=30)
        btn_operations.pack(pady=10)

        btn_exit = tk.Button(self.root, text="Salir", command=self.on_closing, width=30)
        btn_exit.pack(pady=10)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def config_os(self):
        self.clear_window()
        label = tk.Label(self.root, text="Configuracion OS", font=("Arial", 16))
        label.pack(pady=20)

        tk.Label(self.root, text="Seleccionar Algoritmo:").pack(pady=10)
        self.algorithm_selector = ttk.Combobox(self.root, values=["", "FAT32", "NTFS", "EXT"])
        self.algorithm_selector.current(0)
        self.algorithm_selector.pack(pady=10)

        btn_apply_algorithm = tk.Button(self.root, text="Aplicar", command=self.apply_algorithm, width=30)
        btn_apply_algorithm.pack(pady=10)

        btn_set_directory = tk.Button(self.root, text="Establecer Directorio Actual", command=self.set_directory, width=30)
        btn_set_directory.pack(pady=10)

        btn_view_allocation_table = tk.Button(self.root, text="Ver Allocation Table (FAT32)", command=self.view_allocation_table, width=30)
        btn_view_allocation_table.pack(pady=10)

        btn_view_journal = tk.Button(self.root, text="Ver Journal (EXT)", command=self.view_journal, width=30)
        btn_view_journal.pack(pady=10)

        btn_view_mft = tk.Button(self.root, text="Ver MFT (NTFS)", command=self.view_mft, width=30)
        btn_view_mft.pack(pady=10)

        btn_back = tk.Button(self.root, text="Volver", command=self.create_main_menu, width=20)
        btn_back.pack(pady=10)

    def apply_algorithm(self):
        self.selected_algorithm = self.algorithm_selector.get()
        self.calculate_reserved_blocks()
        messagebox.showinfo("Algoritmo Aplicado", f"Algoritmo seleccionado: {self.selected_algorithm}")
        self.update_progress_bar()

    def calculate_reserved_blocks(self):
        """Calcula los bloques reservados según el algoritmo seleccionado"""
        
        #Formula Base: Porcentaje de Reserva= (Size Particion)/ (Size Cluster)
        #En este caso por fines proporcionales se utiliza el porcentaje comun de espacio reservado por File System
        
        if self.selected_algorithm == "FAT32":
            # Suponemos que la Allocation Table ocupa 8% del disco en total (pero existen dos copias por particion)
            self.reserved_blocks = int(self.disk_blocks * 0.16)
        elif self.selected_algorithm == "NTFS":
            # NTFS reserva aproximadamente el 12.5% del espacio del disco para la MFT
            self.reserved_blocks = int(self.disk_blocks * 0.125)
        elif self.selected_algorithm == "EXT":
            # EXT reserva el 5% del espacio total de la partición para el Journal
            self.reserved_blocks = int(self.disk_blocks * 0.05)
        else:
            self.reserved_blocks = 0

        self.used_blocks = self.reserved_blocks

    def set_directory(self):
        new_directory = filedialog.askdirectory(initialdir=self.current_directory, title="Selecciona el Directorio")
        if new_directory:
            self.current_directory = new_directory
            messagebox.showinfo("Directorio Actual", f"Directorio cambiado a: {self.current_directory}")
            
            
            
            
    def view_allocation_table(self):
      if self.selected_algorithm == "FAT32":
        # Crear una ventana para la tabla
        table_window = tk.Toplevel(self.root)
        table_window.title("Tabla de Asignación (FAT32)")

        # Crear un Treeview para mostrar los datos en formato tabular
        columns = ("Archivo", "Bloques", "Ruta")
        tree = ttk.Treeview(table_window, columns=columns, show="headings")
        tree.heading("Archivo", text="Archivo")
        tree.heading("Bloques", text="Bloques")
        tree.heading("Ruta", text="Ruta")

        # Agregar los datos del diccionario a la tabla
        for file, data in self.allocation_table.items():
            tree.insert("", tk.END, values=(file, data['blocks'], data['path']))

        # Mostrar la tabla
        tree.pack(fill="both", expand=True)
      else:
        # Mostrar mensaje de error si el algoritmo no es FAT32
        messagebox.showwarning("Incompatibilidad", "El Algoritmo no Corresponde a este Metodo.")
       
            
    def view_journal(self):
     if self.selected_algorithm == "EXT":
        # Crear una ventana nueva
        journal_window = Toplevel()
        journal_window.title("Journal de Operaciones")

        # Crear un frame para la tabla
        frame = Frame(journal_window)
        frame.pack(fill="both", expand=True)

        # Crear un Treeview
        tree = ttk.Treeview(frame, columns=("Operaciones"), show="headings")
        tree.heading("Operaciones", text="Operaciones")
        tree.pack(fill="both", expand=True)

        # Insertar los contenidos del journal en el Treeview
        for operation in self.journal:
            tree.insert("", "end", values=(operation,))

        # Ajustar el tamaño de la columna
        tree.column("Operaciones", width=300)

        # Botón para cerrar la ventana
        close_button = ttk.Button(journal_window, text="Cerrar", command=journal_window.destroy)
        close_button.pack(pady=10)

     else:
        messagebox.showwarning("Incompatibilidad", "El Algoritmo no Corresponde a este Método.")

            
    def view_mft(self):
        if self.selected_algorithm == "NTFS":
            mft_content = json.dumps(self.mft, indent=4)
            messagebox.showinfo("MFT (NTFS)", f"Master File Table:\n\n{mft_content}")
        else:
            messagebox.showwarning("Incompatibilidad", "El Algoritmo no Corresponde a este Metodo.")

 

    def config_disk(self):
        self.clear_window()
        label = tk.Label(self.root, text="Configuracion Disco Local", font=("Arial", 16))
        label.pack(pady=20)

        size_label = tk.Label(self.root, text="Tamaño", font=("Arial", 14))
        size_label.pack(pady=10)

        self.cluster_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.cluster_label.pack(pady=5)

        self.disk_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.disk_label.pack(pady=5)

        self.partition_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.partition_label.pack(pady=5)
        
        self.filesize_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.filesize_label.pack(pady=5)

        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(pady=30)

        self.update_size_info()
        self.update_progress_bar()
        
        btn_view_structure = tk.Button(self.root, text="Ver Estructura de Directorios", command=self.view_directory_structure, width=30)
        btn_view_structure.pack(pady=50)

        btn_back = tk.Button(self.root, text="Volver", command=self.create_main_menu, width=20)
        btn_back.pack(pady=10)

    def update_size_info(self):
        if self.selected_algorithm == "FAT32":
            cluster_size = "De 512 bytes a 64 KB"
            disk_size = "2 TB"
            partition_size = "32 GB"
            filesize = "4 GB"
        elif self.selected_algorithm == "NTFS":
            cluster_size = "De 512 bytes a 64 KB"
            disk_size = "256 TB"
            partition_size = "2 TB"
            filesize = "16 TB"
        elif self.selected_algorithm == "EXT":
            cluster_size = "De 1 KB a 4 KB"
            disk_size = "1 EB"
            partition_size = "32 TB"
            filesize = "16 TB"
        else:
            cluster_size = "Desconocido"
            disk_size = "Desconocido"
            partition_size = "Desconocido"
            filesize = "Desconocido"

        self.cluster_label.config(text=f"Cluster: {cluster_size}")
        self.disk_label.config(text=f"Disco Duro: {disk_size}")
        self.partition_label.config(text=f"Particion: {partition_size}")
        self.filesize_label.config(text=f"Archivo Maximo: {filesize}")

    def update_progress_bar(self):
        for widget in self.progress_frame.winfo_children():
            widget.destroy()

        total_width = 800
        used_width = int((self.used_blocks / self.disk_blocks) * total_width)

        # Mostrar los bloques reservados por el sistema de archivos
        reserved_width = int((self.reserved_blocks / self.disk_blocks) * total_width)
        reserved_label = tk.Label(
            self.progress_frame,
            text=f"Reservado ({self.reserved_blocks} bloques)",
            bg="blue",
            fg="white",
            width=reserved_width // 3,
            anchor="w"
        )
        reserved_label.pack(side=tk.LEFT, padx=(0, 1))

        # Mostrar los bloques usados por archivos
        if used_width - reserved_width > 0:
            usage_label = tk.Label(
                self.progress_frame,
                text=f"Usado ({self.used_blocks - self.reserved_blocks} bloques)",
                bg="red",
                fg="white",
                width=(used_width - reserved_width) // 10,
                anchor="w"
            )
            usage_label.pack(side=tk.LEFT, padx=(0, 1))

        # Mostrar el espacio libre restante
        free_width = total_width - used_width
        if free_width > 0:
            free_label = tk.Label(
                self.progress_frame,
                text=f"Libre ({self.disk_blocks - self.used_blocks} bloques)",
                bg="green",
                fg="white",
                width=free_width // 10,
                anchor="w"
            )
            free_label.pack(side=tk.LEFT)
            
    def view_directory_structure(self):
        structure = "\n".join(os.listdir(self.current_directory))
        messagebox.showinfo("Estructura de Directorios", f"Contenido de '{self.current_directory}':\n\n{structure}")

    def file_operations(self):
        self.clear_window()
        label = tk.Label(self.root, text="Ejecucion de Operaciones con Archivos", font=("Arial", 16))
        label.pack(pady=20)

        btn_create_file = tk.Button(self.root, text="Crear Archivo", command=self.create_file, width=30)
        btn_create_file.pack(pady=10)

        btn_save_replace_file = tk.Button(self.root, text="Guardar/Reemplazar Archivo", command=self.save_replace_file, width=30)
        btn_save_replace_file.pack(pady=10)

        btn_move_file = tk.Button(self.root, text="Mover Archivo a Otro Directorio", command=self.move_file, width=30)
        btn_move_file.pack(pady=10)

        btn_delete_file = tk.Button(self.root, text="Eliminar Archivo", command=self.delete_file, width=30)
        btn_delete_file.pack(pady=10)

        btn_back = tk.Button(self.root, text="Volver", command=self.create_main_menu, width=20)
        btn_back.pack(pady=10)

    def create_file(self):
        file_name = simpledialog.askstring("Nombre del Archivo", "Introduce el nombre del archivo:")
        blocks = simpledialog.askinteger("Bloques Requeridos", "Introduce la cantidad de bloques que necesita el archivo:", minvalue=1)
        file_content = simpledialog.askstring("Contenido del Archivo", "Introduce el contenido del archivo:")

        if file_name and blocks and file_content is not None:
            if self.used_blocks + blocks <= self.disk_blocks:
                file_path = os.path.join(self.current_directory, file_name)
                try:
                    with open(file_path, 'w') as file:
                        file.write(file_content)

                    # Registrar uso de bloques
                    self.used_blocks += blocks
                    self.block_usage[file_name] = blocks

                    # Actualizar estructuras del sistema de archivos según el algoritmo
                    if self.selected_algorithm == "FAT32":
                        self.allocation_table[file_name] = {'blocks': blocks, 'path': file_path}
                    elif self.selected_algorithm == "EXT":
                        self.journal.append(f"Archivo creado: {file_name}, Bloques: {blocks}, Path: {file_path}")
                    elif self.selected_algorithm == "NTFS":
                        self.mft[file_name] = {'size': blocks, 'blocks': blocks, 'path': file_path}

                    messagebox.showinfo("Archivo Creado", f"Archivo '{file_name}' creado exitosamente con {blocks} bloques.")
                    self.update_progress_bar()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo crear el archivo: {str(e)}")
            else:
                messagebox.showwarning("Error de Espacio", "No hay suficiente espacio disponible para crear el archivo.")

    def save_replace_file(self):
        file_name = simpledialog.askstring("Nombre del Archivo", "Introduce el nombre del archivo para guardar/reemplazar:")
        blocks = simpledialog.askinteger("Bloques Requeridos", "Introduce la cantidad de bloques que necesita el archivo:", minvalue=1)

        if file_name and blocks and self.used_blocks + blocks <= self.disk_blocks:
            file_path = os.path.join(self.current_directory, file_name)
            try:
                with open(file_path, 'w') as file:
                    file.write("Contenido del archivo")

                # Actualizar bloques y registros
                if file_name in self.block_usage:
                    self.used_blocks -= self.block_usage[file_name]  # Liberar los bloques antiguos

                self.used_blocks += blocks
                self.block_usage[file_name] = blocks

                # Actualizar estructuras del sistema de archivos
                if self.selected_algorithm == "FAT32":
                    self.allocation_table[file_name] = {'blocks': blocks, 'path': file_path}
                elif self.selected_algorithm == "EXT":
                    self.journal.append(f"Archivo guardado/reemplazado: {file_name}, Bloques: {blocks}, Path: {file_path}")
                elif self.selected_algorithm == "NTFS":
                    self.mft[file_name] = {'size': blocks, 'blocks': blocks, 'path': file_path}

                messagebox.showinfo("Archivo Guardado", f"Archivo '{file_name}' guardado/reemplazado exitosamente con {blocks} bloques.\nUbicación: {file_path}")
                self.update_progress_bar()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar/reemplazar el archivo: {str(e)}")
        else:
            messagebox.showwarning("Error de Espacio", "No hay suficiente espacio disponible para guardar el archivo.")

    def move_file(self):
        file_name = simpledialog.askstring("Nombre del Archivo", "Introduce el nombre del archivo a mover:")
        new_directory = simpledialog.askstring("Nuevo Directorio", "Introduce la ruta del nuevo directorio:")

        if file_name and new_directory:
            file_path = os.path.join(self.current_directory, file_name)
            new_path = os.path.join(new_directory, file_name)

            try:
                shutil.move(file_path, new_path)

                # Actualizar la ruta en las estructuras internas del sistema de archivos
                if file_name in self.allocation_table:
                    self.allocation_table[file_name]['path'] = new_path
                elif file_name in self.mft:
                    self.mft[file_name]['path'] = new_path
                elif any(file_name in entry for entry in self.journal):
                    self.journal = [entry.replace(file_path, new_path) if file_name in entry else entry for entry in self.journal]

                messagebox.showinfo("Archivo Movido", f"Archivo '{file_name}' movido exitosamente a: {new_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo mover el archivo: {str(e)}")

    def delete_file(self):
        file_name = simpledialog.askstring("Nombre del Archivo", "Introduce el nombre del archivo a eliminar:")

        if file_name:
            file_path = os.path.join(self.current_directory, file_name)
            try:
                os.remove(file_path)

                # Actualizar uso de bloques y estructuras internas
                if file_name in self.block_usage:
                    self.used_blocks -= self.block_usage[file_name]
                    del self.block_usage[file_name]

                if file_name in self.allocation_table:
                    del self.allocation_table[file_name]
                elif file_name in self.mft:
                    del self.mft[file_name]
                elif any(file_name in entry for entry in self.journal):
                    self.journal = [entry for entry in self.journal if file_name not in entry]

                messagebox.showinfo("Archivo Eliminado", f"Archivo '{file_name}' eliminado exitosamente.")
                self.update_progress_bar()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el archivo: {str(e)}")

    def on_closing(self):
        self.save_data()
        self.root.destroy()

    def save_data(self):
        # Guardar los datos de la sesión actual en un archivo JSON
        data = {
            'allocation_table': self.allocation_table,
            'journal': self.journal,
            'mft': self.mft,
            'disk_blocks': self.disk_blocks,
            'used_blocks': self.used_blocks,
            'block_usage': self.block_usage
        }
        with open('filesystem_data.json', 'w') as f:
            json.dump(data, f)

    def load_data(self):
        # Cargar los datos de la sesión anterior desde un archivo JSON
        if os.path.exists('filesystem_data.json'):
            with open('filesystem_data.json', 'r') as f:
                data = json.load(f)
                self.allocation_table = data.get('allocation_table', {})
                self.journal = data.get('journal', [])
                self.mft = data.get('mft', {})
                self.disk_blocks = data.get('disk_blocks', 1000)
                self.used_blocks = data.get('used_blocks', 0)
                self.block_usage = data.get('block_usage', {})
                self.reserved_blocks = data.get('reserved_blocks', 0)
                self.selected_algorithm = data.get('selected_algorithm', "")
        else:
            # Inicializar datos por defecto si el archivo no existe
            self.allocation_table = {}
            self.journal = []
            self.mft = {}
            self.disk_blocks = 1000
            self.used_blocks = 0
            self.block_usage = {}
            self.reserved_blocks = 0
            self.selected_algorithm = ""

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSystemApp(root)
    root.geometry("600x500")
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
