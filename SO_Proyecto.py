import tkinter as tk
from tkinter import Frame, Toplevel, messagebox, simpledialog, filedialog, ttk
import os
import shutil
import json

class FileSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proyecto Final, Sistemas Operativos - Sistema de Archivos")
        self.current_directory = os.getcwd()  # Directorio inicial (Donde está el proyecto)
        self.allocation_table = {}  # Allocation Table FAT32
        self.journal = []  # Journal EXT
        self.mft = {}  # MFT NTFS
        self.disk_blocks = 1000  # N total de bloques(clusters) para la simulación
        self.used_blocks = 0  # Bloques ya usados
        self.block_usage = {}  # Uso de bloques por archivo
        self.reserved_blocks = 0  # Bloques reservados para estructuras de sistema de archivos
        self.selected_algorithm = ""  # Algoritmo seleccionado por el usuario
        self.next_available_block = 1  # Siguiente bloque disponible
        
        # Mapeo de bloques máximos por archivo según el sistema de archivos
        self.max_blocks_per_file = {
            "FAT32": 200,
            "NTFS": 800,
            "EXT": 800
        }
        
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

        tk.Label(self.root, text="Seleccionar Sistema de Archivos:").pack(pady=10)
        self.algorithm_selector = ttk.Combobox(self.root, values=["", "FAT32", "NTFS", "EXT"])
        
        # Establecer la selección previa si existe
        if self.selected_algorithm in ["FAT32", "NTFS", "EXT"]:
            self.algorithm_selector.set(self.selected_algorithm)
        else:
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
        if self.selected_algorithm not in ["FAT32", "NTFS", "EXT"]:
            messagebox.showwarning("Selección Inválida", "Por favor, selecciona un sistema de archivos válido.")
            return

        self.calculate_reserved_blocks()
        messagebox.showinfo("Sistema Aplicado", f"Sistema de archivos seleccionado: {self.selected_algorithm}")
        self.update_size_info()
        self.update_progress_bar()
        self.save_data()  # Guardar los cambios inmediatamente

    def calculate_reserved_blocks(self):
        """Calcula los bloques reservados según el algoritmo seleccionado"""
        
        # Fórmula Base: Porcentaje de Reserva = (Size Particion) / (Size Cluster)
        # En este caso, se utiliza el porcentaje común de espacio reservado por File System
        
        if self.selected_algorithm == "FAT32":
            # Suponemos que la Allocation Table ocupa 16% del disco en total
            self.reserved_blocks = int(self.disk_blocks * 0.16)
        elif self.selected_algorithm == "NTFS":
            # NTFS reserva aproximadamente el 12.5% del espacio del disco para la MFT
            self.reserved_blocks = int(self.disk_blocks * 0.125)
        elif self.selected_algorithm == "EXT":
            # EXT reserva el 5% del espacio total de la partición para el Journal
            self.reserved_blocks = int(self.disk_blocks * 0.05)
        else:
            self.reserved_blocks = 0

        # Asegurarse de que used_blocks incluye reserved_blocks
        if self.used_blocks < self.reserved_blocks:
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

            # Crear un Treeview para mostrar los datos
            columns = ("Archivo", "Bloques", "Rango de Bloques", "Ruta")
            tree = ttk.Treeview(table_window, columns=columns, show="headings")
            tree.heading("Archivo", text="Archivo")
            tree.heading("Bloques", text="Bloques")
            tree.heading("Rango de Bloques", text="Rango de Bloques")
            tree.heading("Ruta", text="Ruta")

            # Agregar los datos del diccionario a la tabla
            for file, data in self.allocation_table.items():
                blocks = data['blocks']
                start_block = data['start_block']
                end_block = data['end_block']
                rango = f"{start_block}-{end_block}"
                tree.insert("", tk.END, values=(file, blocks, rango, data['path']))

            # Mostrar la tabla
            tree.pack(fill="both", expand=True)
        else:
            # Mostrar mensaje de error si el algoritmo no es FAT32
            messagebox.showwarning("Incompatibilidad", "El Sistema de Archivos seleccionado no es FAT32.")

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
            messagebox.showwarning("Incompatibilidad", "El Sistema de Archivos seleccionado no es EXT.")

    def view_mft(self):
        if self.selected_algorithm == "NTFS":
            # Convertir el contenido de la MFT a un formato más legible para la tabla
            mft_data = []
            for file, data in self.mft.items():
                mft_data.append([file, data["size"], data["blocks"], data["path"]])

            # Crear una ventana para la tabla
            mft_window = tk.Toplevel(self.root)
            mft_window.title("Tabla Maestra de Archivos (MFT)")

            # Crear un Treeview para mostrar los datos en formato tabular
            columns = ("Nombre Archivo", "Tamaño", "Bloques", "Ruta")
            tree = ttk.Treeview(mft_window, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col)
            tree.pack(fill="both", expand=True)

            # Insertar los datos de la MFT en la tabla
            for row in mft_data:
                tree.insert("", "end", values=row)

            # Ajustar el ancho de las columnas para una mejor visualización
            tree.column("Nombre Archivo", width=200, anchor="w")
            tree.column("Tamaño", width=100, anchor="center")
            tree.column("Bloques", width=100, anchor="center")
            tree.column("Ruta", width=300, anchor="w")
        else:
            messagebox.showwarning("Incompatibilidad", "El Sistema de Archivos seleccionado no es NTFS.")

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
            filesize = f"Máximo {self.max_blocks_per_file['FAT32']} bloques"
        elif self.selected_algorithm == "NTFS":
            cluster_size = "De 512 bytes a 64 KB"
            disk_size = "256 TB"
            partition_size = "2 TB"
            filesize = f"Máximo {self.max_blocks_per_file['NTFS']} bloques"
        elif self.selected_algorithm == "EXT":
            cluster_size = "De 1 KB a 4 KB"
            disk_size = "1 EB"
            partition_size = "32 TB"
            filesize = f"Máximo {self.max_blocks_per_file['EXT']} bloques"
        else:
            cluster_size = "Desconocido"
            disk_size = "Desconocido"
            partition_size = "Desconocido"
            filesize = "Desconocido"

        self.cluster_label.config(text=f"Cluster: {cluster_size}")
        self.disk_label.config(text=f"Disco Duro: {disk_size}")
        self.partition_label.config(text=f"Partición: {partition_size}")
        self.filesize_label.config(text=f"Archivo Máximo: {filesize}")

    def update_progress_bar(self):
        # Verificar si progress_frame existe
        if not hasattr(self, 'progress_frame'):
            return  # Salir si progress_frame no está creado

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
            width=reserved_width // 10,  # Ajustar el ancho para visualización
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
                width=(used_width - reserved_width) // 10,  # Ajustar el ancho para visualización
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
                width=free_width // 10,  # Ajustar el ancho para visualización
                anchor="w"
            )
            free_label.pack(side=tk.LEFT)

    def view_directory_structure(self):
        structure = "\n".join(os.listdir(self.current_directory))
        messagebox.showinfo("Estructura de Directorios", f"Contenido de '{self.current_directory}':\n\n{structure}")

    def file_operations(self):
        self.clear_window()
        label = tk.Label(self.root, text="Ejecución de Operaciones con Archivos", font=("Arial", 16))
        label.pack(pady=20)

        btn_create_file = tk.Button(self.root, text="Crear Archivo", command=self.create_file, width=30)
        btn_create_file.pack(pady=10)

        btn_save_replace_file = tk.Button(self.root, text="Guardar/Reemplazar Archivo", command=self.save_replace_file, width=30)
        btn_save_replace_file.pack(pady=10)

        btn_move_file = tk.Button(self.root, text="Mover Archivo a Otro Directorio", command=self.move_file, width=30)
        btn_move_file.pack(pady=10)

        btn_delete_file = tk.Button(self.root, text="Eliminar Archivo", command=self.delete_file, width=30)
        btn_delete_file.pack(pady=10)
        
        # Nuevo Botón para Crear Carpetas
        btn_create_folder = tk.Button(self.root, text="Crear Carpeta", command=self.create_folder, width=30)
        btn_create_folder.pack(pady=10)

        btn_back = tk.Button(self.root, text="Volver", command=self.create_main_menu, width=20)
        btn_back.pack(pady=10)

    def create_file(self):
        file_name = simpledialog.askstring("Nombre del Archivo", "Introduce el nombre del archivo:")
        blocks = simpledialog.askinteger("Bloques Requeridos", "Introduce la cantidad de bloques que necesita el archivo:", minvalue=1)
        file_content = simpledialog.askstring("Contenido del Archivo", "Introduce el contenido del archivo:")

        if file_name and blocks and file_content is not None:
            max_blocks = self.max_blocks_per_file.get(self.selected_algorithm, 0)
            if blocks > max_blocks:
                messagebox.showwarning("Exceso de Bloques", f"El archivo excede el número máximo de bloques permitidos para {self.selected_algorithm} ({max_blocks} bloques).")
                return

            if self.used_blocks + blocks <= self.disk_blocks:
                file_path = os.path.join(self.current_directory, file_name)
                try:
                    with open(file_path, 'w') as file:
                        file.write(file_content)

                    # Registrar uso de bloques
                    self.used_blocks += blocks
                    start_block = self.next_available_block
                    end_block = self.next_available_block + blocks - 1
                    self.block_usage[file_name] = blocks
                    self.next_available_block += blocks

                    # Actualizar estructuras del sistema de archivos según el algoritmo
                    if self.selected_algorithm == "FAT32":
                        self.allocation_table[file_name] = {
                            'blocks': blocks,
                            'start_block': start_block,
                            'end_block': end_block,
                            'path': file_path
                        }
                    elif self.selected_algorithm == "EXT":
                        self.journal.append(f"Archivo creado: {file_name}, Bloques: {blocks}, Path: {file_path}")
                    elif self.selected_algorithm == "NTFS":
                        self.mft[file_name] = {
                            'size': blocks,
                            'blocks': blocks,
                            'path': file_path
                        }

                    messagebox.showinfo("Archivo Creado", f"Archivo '{file_name}' creado exitosamente con {blocks} bloques.\nRango de Bloques: {start_block}-{end_block}")
                    self.update_progress_bar()
                    self.save_data()  # Guardar los cambios
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo crear el archivo: {str(e)}")
            else:
                messagebox.showwarning("Error de Espacio", "No hay suficiente espacio disponible para crear el archivo.")

    def save_replace_file(self):
        file_name = simpledialog.askstring("Nombre del Archivo", "Introduce el nombre del archivo para guardar/reemplazar:")
        blocks = simpledialog.askinteger("Bloques Requeridos", "Introduce la cantidad de bloques que necesita el archivo:", minvalue=1)

        if file_name and blocks:
            max_blocks = self.max_blocks_per_file.get(self.selected_algorithm, 0)
            if blocks > max_blocks:
                messagebox.showwarning("Exceso de Bloques", f"El archivo excede el número máximo de bloques permitidos para {self.selected_algorithm} ({max_blocks} bloques).")
                return

            file_path = os.path.join(self.current_directory, file_name)
            existing_blocks = self.block_usage.get(file_name, 0)

            # Verificar si hay suficiente espacio
            if self.used_blocks - existing_blocks + blocks > self.disk_blocks:
                messagebox.showwarning("Error de Espacio", "No hay suficiente espacio disponible para guardar/reemplazar el archivo.")
                return

            try:
                with open(file_path, 'w') as file:
                    file.write("Contenido del archivo")  # Puedes modificar esto para permitir al usuario ingresar contenido

                # Actualizar bloques y registros
                self.used_blocks = self.used_blocks - existing_blocks + blocks
                start_block = self.next_available_block
                end_block = self.next_available_block + blocks - 1
                self.block_usage[file_name] = blocks
                self.next_available_block += blocks

                # Actualizar estructuras del sistema de archivos
                if self.selected_algorithm == "FAT32":
                    self.allocation_table[file_name] = {
                        'blocks': blocks,
                        'start_block': start_block,
                        'end_block': end_block,
                        'path': file_path
                    }
                elif self.selected_algorithm == "EXT":
                    self.journal.append(f"Archivo guardado/reemplazado: {file_name}, Bloques: {blocks}, Path: {file_path}")
                elif self.selected_algorithm == "NTFS":
                    self.mft[file_name] = {
                        'size': blocks,
                        'blocks': blocks,
                        'path': file_path
                    }

                messagebox.showinfo("Archivo Guardado", f"Archivo '{file_name}' guardado/reemplazado exitosamente con {blocks} bloques.\nRango de Bloques: {start_block}-{end_block}\nUbicación: {file_path}")
                self.update_progress_bar()
                self.save_data()  # Guardar los cambios
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar/reemplazar el archivo: {str(e)}")
        else:
            messagebox.showwarning("Entrada Inválida", "Por favor, completa todos los campos.")

    def move_file(self):
        file_name = simpledialog.askstring("Nombre del Archivo", "Introduce el nombre del archivo a mover:")
        new_directory = simpledialog.askstring("Nuevo Directorio", "Introduce la ruta del nuevo directorio:")

        if file_name and new_directory:
            file_path = os.path.join(self.current_directory, file_name)
            new_path = os.path.join(new_directory, file_name)

            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"El archivo '{file_name}' no existe en el directorio actual.")
                return

            try:
                shutil.move(file_path, new_path)

                # Actualizar la ruta en las estructuras internas del sistema de archivos
                if self.selected_algorithm == "FAT32":
                    if file_name in self.allocation_table:
                        self.allocation_table[file_name]['path'] = new_path
                elif self.selected_algorithm == "NTFS":
                    if file_name in self.mft:
                        self.mft[file_name]['path'] = new_path
                elif self.selected_algorithm == "EXT":
                    self.journal = [entry.replace(file_path, new_path) if file_name in entry else entry for entry in self.journal]

                messagebox.showinfo("Archivo Movido", f"Archivo '{file_name}' movido exitosamente a: {new_path}")
                self.save_data()  # Guardar los cambios
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo mover el archivo: {str(e)}")

    def delete_file(self):
        file_name = simpledialog.askstring("Nombre del Archivo", "Introduce el nombre del archivo a eliminar:")

        if file_name:
            file_path = os.path.join(self.current_directory, file_name)
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"El archivo '{file_name}' no existe en el directorio actual.")
                return

            try:
                os.remove(file_path)

                # Actualizar uso de bloques y estructuras internas
                if file_name in self.block_usage:
                    self.used_blocks -= self.block_usage[file_name]
                    del self.block_usage[file_name]

                if self.selected_algorithm == "FAT32":
                    if file_name in self.allocation_table:
                        del self.allocation_table[file_name]
                elif self.selected_algorithm == "NTFS":
                    if file_name in self.mft:
                        del self.mft[file_name]
                elif self.selected_algorithm == "EXT":
                    self.journal = [entry for entry in self.journal if file_name not in entry]

                messagebox.showinfo("Archivo Eliminado", f"Archivo '{file_name}' eliminado exitosamente.")
                self.update_progress_bar()
                self.save_data()  # Guardar los cambios
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el archivo: {str(e)}")

    def create_folder(self):
        folder_name = simpledialog.askstring("Nombre de la Carpeta", "Introduce el nombre de la carpeta:")
        
        if folder_name:
            # Validar el nombre de la carpeta (opcional)
            if any(char in folder_name for char in r'<>:"/\|?*'):
                messagebox.showerror("Nombre Inválido", "El nombre de la carpeta contiene caracteres inválidos.")
                return

            folder_path = os.path.join(self.current_directory, folder_name)
            
            if os.path.exists(folder_path):
                messagebox.showwarning("Carpeta Existente", f"La carpeta '{folder_name}' ya existe en el directorio actual.")
                return
            
            try:
                os.mkdir(folder_path)
                messagebox.showinfo("Carpeta Creada", f"Carpeta '{folder_name}' creada exitosamente en '{self.current_directory}'.")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear la carpeta: {str(e)}")
        else:
            messagebox.showwarning("Entrada Inválida", "El nombre de la carpeta no puede estar vacío.")

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
            'block_usage': self.block_usage,
            'reserved_blocks': self.reserved_blocks,
            'selected_algorithm': self.selected_algorithm,
            'next_available_block': self.next_available_block  # Añadido
        }
        with open('filesystem_data.json', 'w') as f:
            json.dump(data, f, indent=4)

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
                self.next_available_block = data.get('next_available_block', 1)  # Añadido
                
                # Recalcular bloques reservados si se ha seleccionado un algoritmo
                if self.selected_algorithm:
                    self.calculate_reserved_blocks()
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
            self.next_available_block = 1  # Añadido

        # **Eliminar la llamada a update_progress_bar aquí**
        # self.update_progress_bar()

    def update_progress_bar(self):
        # Verificar si progress_frame existe
        if not hasattr(self, 'progress_frame'):
            return  # Salir si progress_frame no está creado

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
            width=reserved_width // 10,  # Ajustar el ancho para visualización
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
                width=(used_width - reserved_width) // 10,  # Ajustar el ancho para visualización
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

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSystemApp(root)
    root.geometry("600x500")
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
