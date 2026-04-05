import { spawn } from "node:child_process";

const npmCommand = process.platform === "win32" ? "npm.cmd" : "npm";

function prefixStream(stream, label) {
  let buffer = "";

  stream.on("data", (chunk) => {
    buffer += chunk.toString();
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      process.stdout.write(`[${label}] ${line}\n`);
    }
  });

  stream.on("end", () => {
    if (buffer.length > 0) {
      process.stdout.write(`[${label}] ${buffer}\n`);
    }
  });
}

function startProcess(label, script) {
  const child = spawn(npmCommand, ["run", script], {
    stdio: ["inherit", "pipe", "pipe"],
    env: process.env,
  });

  prefixStream(child.stdout, label);
  prefixStream(child.stderr, label);
  return child;
}

const children = [
  { label: "backend", child: startProcess("backend", "backend") },
  { label: "frontend", child: startProcess("frontend", "frontend") },
];

let shuttingDown = false;

function stopChildren(signal = "SIGTERM") {
  if (shuttingDown) return;
  shuttingDown = true;

  for (const { child } of children) {
    if (!child.killed) {
      child.kill(signal);
    }
  }
}

for (const { label, child } of children) {
  child.on("exit", (code, signal) => {
    if (!shuttingDown) {
      stopChildren();
      if (signal) {
        console.error(`[${label}] exited due to signal ${signal}`);
        process.exit(1);
      }
      process.exit(code ?? 1);
    }
  });
}

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => {
    stopChildren(signal);
    process.exit(0);
  });
}
