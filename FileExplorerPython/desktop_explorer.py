# /full/path/to/your/project/desktop_explorer.py
import tkinter as tk
from tkinter import ttk, font # Import font module
from tkinter import messagebox
import os
import pathlib
import subprocess
import sys
import platform # Import platform module to check OS

class FileExplorerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cross-Platform File Explorer")
        self.geometry("800x600") # Even larger default size for better spacing

        # --- Style Configuration ---
        self.style = ttk.Style(self)
        # Try different themes: 'clam', 'alt', 'default', 'vista' (Windows), 'aqua' (macOS)
        available_themes = self.style.theme_names()
        # print("Available themes:", available_themes) # Uncomment to see available themes
        preferred_themes = ['clam', 'vista', 'aqua', 'alt', 'default'] # Order of preference
        for theme in preferred_themes:
            if theme in available_themes:
                self.style.theme_use(theme)
                break

        # Use pathlib for robust and cross-platform path manipulation
        try:
            # Start at the user's home directory
            self.current_path = pathlib.Path.home()
            if not self.current_path.is_dir(): # Fallback if home dir isn't accessible
                 self.current_path = pathlib.Path.cwd()
        except Exception:
             # Generic fallback if home() fails for any reason
             self.current_path = pathlib.Path.cwd()

        # --- Define Fonts ---
        self.default_font = font.nametofont("TkDefaultFont") # Get default font
        self.default_font.configure(size=10) # Set default size
        self.list_font = font.Font(family=self.default_font.cget("family"), size=11)
        self.path_font = font.Font(family=self.default_font.cget("family"), size=10)

        # Apply default font to root window
        self.option_add("*Font", self.default_font)

        # --- UI Elements ---
        # Frame for path display and navigation buttons
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=(10, 5)) # More vertical padding top

        self.up_button = ttk.Button(top_frame, text="Up", command=self.go_up, width=5)
        self.up_button.pack(side=tk.LEFT, padx=(0, 5))

        self.home_button = ttk.Button(top_frame, text="Home", command=self.go_home, width=6)
        self.home_button.pack(side=tk.LEFT, padx=(0, 10))

        self.path_var = tk.StringVar(value=str(self.current_path))
        self.path_entry = ttk.Entry(top_frame, textvariable=self.path_var, state='readonly', font=self.path_font)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.style.configure("TEntry", padding=(5, 3)) # Add internal padding to entry

        # Main frame for the listbox and scrollbar
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10)) # Add padding

        # Configure Listbox style (e.g., selection color)
        self.style.map("TListbox",
                       background=[('selected', '#0078D7'), ('!selected', 'white')], # Example: Blue selection like Windows Explorer
                       foreground=[('selected', 'white'), ('!selected', 'black')])

        self.scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=self.scrollbar.set,
            selectmode=tk.SINGLE,
            font=self.list_font, # Use defined list font
            # Apply some ttk styling if possible (depends on theme)
            # background=self.style.lookup("TListbox", "background"), # Get theme background
            # foreground=self.style.lookup("TListbox", "foreground"), # Get theme foreground
            # selectbackground=self.style.lookup("TListbox", "selectbackground"), # Get theme selection background
            # selectforeground=self.style.lookup("TListbox", "selectforeground")  # Get theme selection foreground
        )
        self.scrollbar.config(command=self.listbox.yview)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Bindings ---
        self.listbox.bind("<Double-Button-1>", self.on_item_double_click) # Double click
        self.listbox.bind("<Return>", self.on_item_double_click) # Enter key also navigates/opens

        # --- Status Bar (Optional but nice) ---
        self.status_var = tk.StringVar(value="Ready")
        # Use a Frame for better background control if needed, or just style the Label
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.FLAT, anchor=tk.W, padding=(5, 3), background="#ECECEC") # Lighter background, flat relief
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Initial Population ---
        self.update_list()

    def update_list(self):
        """Updates the listbox with the contents of the current_path."""
        self.listbox.delete(0, tk.END) # Clear existing items
        self.path_var.set(str(self.current_path))
        self.status_var.set(f"Listing: {self.current_path}")

        items = []
        try:
            # Separate directories and files
            dirs = []
            files = []
            for item in self.current_path.iterdir():
                # Basic check if item is hidden (can be platform dependent)
                is_hidden = item.name.startswith('.') or (platform.system() == "Windows" and item.stat().st_file_attributes & 2 != 0)
                if is_hidden:
                    continue # Skip hidden files/folders for simplicity

                if item.is_dir():
                    # Consider using Unicode symbols or icons later
                    dirs.append(f"📁 {item.name}") # Folder symbol
                else:
                    # Optionally add size or modification date here
                    files.append(f"📄 {item.name}") # Document symbol

            # Sort them alphabetically, directories first
            dirs.sort(key=str.lower)
            files.sort(key=str.lower)
            items = dirs + files

        except PermissionError:
            messagebox.showerror("Permission Error", f"Cannot access directory:\n{self.current_path}\n\nPlease check permissions.")
            self.status_var.set(f"Permission denied: {self.current_path}")
            # Attempt to go up if possible, otherwise stay put but show error
            parent = self.current_path.parent
            if parent != self.current_path:
                self.current_path = parent
                self.update_list() # Try updating parent list
            return # Stop processing this directory
        except FileNotFoundError:
             messagebox.showerror("Not Found", f"Path does not exist:\n{self.current_path}")
             self.status_var.set(f"Path not found: {self.current_path}")
             self.go_home() # Go back to home directory
             return
        except OSError as e: # Catch other OS-level errors (e.g., drive not ready)
             messagebox.showerror("OS Error", f"Could not read directory:\n{self.current_path}\n\nError: {e}")
             self.status_var.set(f"OS Error accessing: {self.current_path}")
             # Attempt to go up
             parent = self.current_path.parent
             if parent != self.current_path:
                 self.current_path = parent
                 self.update_list()
             return
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while listing files:\n{e}")
            self.status_var.set("Unexpected error occurred")
            self.go_home() # Go home on unexpected errors
            return


        # Populate listbox
        if not items:
            self.listbox.insert(tk.END, " (Directory is empty)")
            self.listbox.itemconfig(tk.END, {'foreground': 'grey'}) # Use foreground for color
        else:
            for item in items:
                self.listbox.insert(tk.END, item)

        # Enable/disable Up button
        # Check if the parent is the same as the current path (indicates root)
        if self.current_path == self.current_path.parent:
             self.up_button.config(state=tk.DISABLED)
        else:
             self.up_button.config(state=tk.NORMAL)

        self.status_var.set(f"Listed {len(items)} items in: {self.current_path}")


    def go_up(self):
        """Navigates to the parent directory."""
        parent = self.current_path.parent
        # Check if parent exists and is different from current path
        if parent != self.current_path and parent.exists():
            self.current_path = parent
            self.update_list()
        else:
            # Handle cases like trying to go up from root or if parent doesn't exist
            self.status_var.set("Cannot go further up.")
            self.up_button.config(state=tk.DISABLED) # Disable button if at root


    def go_home(self):
        """Navigates to the user's home directory."""
        try:
            home_path = pathlib.Path.home()
            if home_path.is_dir():
                self.current_path = home_path
                self.update_list()
            else:
                 messagebox.showwarning("Home Not Found", "Could not determine or access the home directory.")
                 self.status_var.set("Home directory not accessible.")
        except Exception as e:
             messagebox.showerror("Error", f"Failed to navigate home: {e}")
             self.status_var.set("Error navigating home.")


    def on_item_double_click(self, event=None):
        """Handles double-clicking or pressing Enter on an item."""
        selection_indices = self.listbox.curselection()
        if not selection_indices:
            return # Nothing selected

        selected_item_text = self.listbox.get(selection_indices[0])

        # Handle the "(Directory is empty)" message
        if selected_item_text.strip() == "(Directory is empty)":
            return

        # Remove the prefix symbol and space (adjust index if symbols change)
        if selected_item_text.startswith("📁 ") or selected_item_text.startswith("📄 "):
            item_name = selected_item_text[2:] # Correct slice index for 2-character prefix
        else:
            # Should not happen with current logic, but handle defensively
            self.status_var.set(f"Unknown item format: {selected_item_text}")
            return

        target_path = self.current_path / item_name

        try:
            # Use resolve() to handle symbolic links correctly and get absolute path
            resolved_path = target_path.resolve()

            if resolved_path.is_dir():
                self.current_path = resolved_path
                self.update_list()
            elif resolved_path.is_file():
                # Try to open the file with the default application
                self.open_file(resolved_path)
            else:
                # This might happen if the item was deleted between listing and clicking
                messagebox.showwarning("Not Found", f"Item no longer exists or is not a file/directory:\n{target_path}")
                self.update_list() # Refresh the list

        except PermissionError:
             messagebox.showerror("Permission Error", f"Cannot access:\n{target_path}")
             self.status_var.set(f"Permission denied: {target_path.name}")
        except FileNotFoundError:
             messagebox.showerror("Not Found", f"Item no longer exists:\n{target_path}")
             self.status_var.set(f"Not found: {target_path.name}")
             self.update_list() # Refresh list
        except Exception as e:
             messagebox.showerror("Error", f"Could not open or access item:\n{target_path}\n\nError: {e}")
             self.status_var.set(f"Error accessing: {target_path.name}")


    def open_file(self, filepath):
        """Opens a file using the OS default application in a cross-platform way."""
        try:
            self.status_var.set(f"Opening: {filepath.name}...")
            current_os = platform.system()

            if current_os == "Windows":
                os.startfile(filepath) # Recommended way on Windows
            elif current_os == "Darwin": # macOS
                subprocess.run(["open", str(filepath)], check=True) # Use subprocess.run for better error checking
            else: # Linux and other Unix-like systems
                subprocess.run(["xdg-open", str(filepath)], check=True)

            # Brief pause allows OS to potentially show feedback before status clears
            self.after(500, lambda: self.status_var.set(f"Opened: {filepath.name}"))

        except FileNotFoundError:
             # Specific error if 'open' or 'xdg-open' command isn't found
             messagebox.showerror("Command Not Found", f"Could not find the command to open files on this system ('{ 'open' if current_os == 'Darwin' else 'xdg-open'}').")
             self.status_var.set("Error: Open command not found.")
        except subprocess.CalledProcessError as e:
             # Error if the command fails (e.g., file type association missing)
             messagebox.showerror("Open Error", f"Failed to open file '{filepath.name}' with the default application.\n\nError: {e}")
             self.status_var.set(f"Error opening: {filepath.name}")
        except Exception as e:
             # Catch-all for other potential errors (like os.startfile issues)
             messagebox.showerror("Open Error", f"An unexpected error occurred while trying to open '{filepath.name}':\n{e}")
             self.status_var.set(f"Error opening: {filepath.name}")


if __name__ == "__main__":
    # Ensures high-DPI awareness on Windows if possible
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except ImportError: # Not Windows or ctypes not available
        pass
    except AttributeError: # Older Windows version without SetProcessDpiAwareness
        try:
             windll.user32.SetProcessDPIAware()
        except Exception:
             pass # Ignore if DPI awareness setting fails

    app = FileExplorerApp()
    app.mainloop()
