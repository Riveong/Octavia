import { mount } from "svelte";
import "./app.css";
import App from "./App.svelte";

declare const Neutralino: any;

Neutralino.init();

Neutralino.events.on("windowClose", () => {
  Neutralino.app.exit();
});

const app = mount(App, { target: document.getElementById("app")! });

export default app;
