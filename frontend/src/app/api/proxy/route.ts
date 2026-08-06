import { NextRequest, NextResponse } from "next/server";

const ALLOWED_HOSTNAMES = [
  "cdninstagram.com",
  "fbcdn.net",
  "tiktokcdn.com",
  "tiktokcdn-us.com",
  "tiktokcdn-eu.com",
  "ibyteimg.com",
  "ytimg.com",
  "ggpht.com",
];

const FETCH_TIMEOUT_MS = 10_000;
const MAX_REDIRECTS = 3;

// These CDNs enforce hotlink protection and 403 requests without a Referer
// matching the platform the CDN belongs to.
const REFERER_BY_HOSTNAME_SUFFIX: [string, string][] = [
  ["cdninstagram.com", "https://www.instagram.com/"],
  ["fbcdn.net", "https://www.instagram.com/"],
  ["tiktokcdn.com", "https://www.tiktok.com/"],
  ["tiktokcdn-us.com", "https://www.tiktok.com/"],
  ["tiktokcdn-eu.com", "https://www.tiktok.com/"],
  ["ibyteimg.com", "https://www.tiktok.com/"],
  ["ytimg.com", "https://www.youtube.com/"],
  ["ggpht.com", "https://www.youtube.com/"],
];

function isAllowedHostname(hostname: string): boolean {
  return ALLOWED_HOSTNAMES.some(
    (domain) => hostname === domain || hostname.endsWith(`.${domain}`)
  );
}

function refererFor(hostname: string): string | undefined {
  return REFERER_BY_HOSTNAME_SUFFIX.find(
    ([domain]) => hostname === domain || hostname.endsWith(`.${domain}`)
  )?.[1];
}

export async function GET(req: NextRequest) {
  const url = req.nextUrl.searchParams.get("url");
  if (!url) return new NextResponse("Missing url", { status: 400 });

  let parsed: URL;
  try {
    parsed = new URL(url);
  } catch {
    return new NextResponse("Invalid url", { status: 400 });
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

  try {
    for (let redirects = 0; ; redirects++) {
      if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
        return new NextResponse("Unsupported protocol", { status: 400 });
      }

      if (!isAllowedHostname(parsed.hostname)) {
        return new NextResponse("Host not allowed", { status: 403 });
      }

      const headers: Record<string, string> = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
      };
      const referer = refererFor(parsed.hostname);
      if (referer) headers["Referer"] = referer;

      const res = await fetch(parsed.toString(), {
        headers,
        redirect: "manual",
        signal: controller.signal,
      });

      if (res.status >= 300 && res.status < 400) {
        const location = res.headers.get("location");
        if (!location || redirects >= MAX_REDIRECTS) {
          return new NextResponse("Redirect not allowed", { status: 502 });
        }
        // Re-validate the redirect target on the next loop iteration —
        // an allowlisted host can't use a redirect to send us elsewhere.
        parsed = new URL(location, parsed);
        continue;
      }

      if (!res.ok) throw new Error("Failed to fetch image");

      const contentType = res.headers.get("content-type") || "";
      if (!contentType.startsWith("image/")) {
        return new NextResponse("Unexpected content type", { status: 502 });
      }

      const buffer = await res.arrayBuffer();

      return new NextResponse(buffer, {
        headers: {
          "Content-Type": contentType,
          "Cache-Control": "public, max-age=86400", // Cache for 24 hours
        },
      });
    }
  } catch (error) {
    return new NextResponse("Error fetching image", { status: 500 });
  } finally {
    clearTimeout(timeout);
  }
}
