export const getDomainFromUrl = (url: string | null) => {
  if (!url) return "Manual";
  try {
    const hostname = new URL(url).hostname.toLowerCase();
    if (hostname.includes("instagram.com")) return "Instagram";
    if (hostname.includes("tiktok.com")) return "TikTok";
    if (hostname.includes("youtube.com") || hostname.includes("youtu.be")) return "YouTube";
    return "Other";
  } catch (e) {
    return "Other";
  }
};
