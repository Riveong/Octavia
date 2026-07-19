export interface Toast {
  id: number;
  type: "success" | "error" | "info";
  message: string;
}

let nextId = 1;

class ToastStore {
  items = $state<Toast[]>([]);

  show(type: Toast["type"], message: string, ms = 3500): void {
    const id = nextId++;
    this.items.push({ id, type, message });
    setTimeout(() => this.dismiss(id), ms);
  }

  success(message: string): void {
    this.show("success", message);
  }

  error(message: string): void {
    this.show("error", message, 6000);
  }

  dismiss(id: number): void {
    this.items = this.items.filter((t) => t.id !== id);
  }
}

export const toast = new ToastStore();
