export const IN_PROGRESS = [
  {
    id: 'analyze-tab-agent',
    title: 'Analyze Tab vs Agent Usage P…',
    subtext: 'Fetching data',
    status: 'in_progress',
  },
  {
    id: 'plan-mission-control',
    title: 'Plan Mission Control',
    subtext: 'Generating plan',
    status: 'in_progress',
  },
];

export const READY_FOR_REVIEW = [
  {
    id: 'build-landing-page',
    title: 'Build Landing Page',
    time: 'now',
    subtext: 'Done. Fonts preload in the head,…',
    status: 'done',
  },
  {
    id: 'pytorch-mnist',
    title: 'PyTorch MNIST Experim…',
    time: '10m ago',
    status: 'done',
  },
  {
    id: 'cursor-rules',
    title: 'Set up Cursor Rules for …',
    time: '30m ago',
    status: 'done',
  },
  {
    id: 'bioinformatics',
    title: 'Bioinformatics Tools',
    time: '45m ago',
    diff: { add: 135, remove: 21 },
    status: 'done',
  },
];

export const TASK_DETAILS = {
  'build-landing-page': {
    title: 'Build Landing Page',
    prompt: 'make a landing page based on attached docs explaining what we do',
    meta: ['Read about-acme.md', 'Read brand-guidelines.pdf', 'Thought 6s'],
    response: "I'll create a minimal, serif-based landing page that matches your brand voice.",
    files: [
      { path: 'app/page.tsx', added: 52, removed: 0 },
      { path: 'app/globals.css', added: 18, removed: 0 },
    ],
    summary:
      'Done. Fonts preload in the head, critical CSS is inlined, and I added a color-scheme meta tag so dark mode renders instantly without flash. 280ms first paint.',
  },
  'pytorch-mnist': {
    title: 'PyTorch MNIST Experim…',
    prompt: 'Train a simple MNIST classifier and log accuracy',
    meta: ['Read train.py', 'Thought 4s'],
    response: "I'll set up a baseline CNN and track validation accuracy each epoch.",
    files: [{ path: 'train.py', added: 87, removed: 3 }],
    summary: 'Done. Best validation accuracy 98.2% after 10 epochs.',
  },
  'cursor-rules': {
    title: 'Set up Cursor Rules for …',
    prompt: 'Add project rules for TypeScript and testing conventions',
    meta: ['Searched .cursor/rules', 'Thought 3s'],
    response: "I'll add rules for imports, component structure, and test patterns.",
    files: [{ path: '.cursor/rules/typescript.mdc', added: 42, removed: 0 }],
    summary: 'Done. Rules cover naming, file layout, and preferred test utilities.',
  },
  'bioinformatics': {
    title: 'Bioinformatics Tools',
    prompt: 'Build CLI tools for sequence alignment and FASTA parsing',
    meta: ['Read requirements.txt', 'Read existing utils/', 'Thought 8s'],
    response: "I'll add alignment and parsing modules with a shared CLI entry point.",
    files: [
      { path: 'tools/align.py', added: 78, removed: 12 },
      { path: 'tools/fasta.py', added: 57, removed: 9 },
    ],
    summary: 'Done. CLI supports batch alignment and exports results as CSV.',
  },
  'analyze-tab-agent': {
    title: 'Analyze Tab vs Agent Usage P…',
    prompt: 'Compare Tab and Agent usage across the team this month',
    meta: ['Fetching data…'],
    status: 'in_progress',
  },
  'plan-mission-control': {
    title: 'Plan Mission Control',
    prompt: 'Draft a plan for a mission control dashboard',
    meta: ['Generating plan…'],
    status: 'in_progress',
  },
};
