export {};

declare global {
  interface Window {
    api: {
      detectFace: () => Promise<string>;
    };
  }
}