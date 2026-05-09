import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: process.env.VITE_DEPLOY_BASE || "/WEBPAGE-/",
  plugins: [react()],
});
