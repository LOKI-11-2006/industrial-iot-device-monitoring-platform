let currentAccessToken: string | null = null;

export const accessTokenStore = Object.freeze({
  get: () => currentAccessToken,
  set: (accessToken: string) => {
    currentAccessToken = accessToken;
  },
  clear: () => {
    currentAccessToken = null;
  },
});
