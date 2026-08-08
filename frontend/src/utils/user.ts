/**
 * COMPAREX User Profile & Display Name Helpers
 */

export interface UserLike {
  name?: string | null;
  full_name?: string | null;
  username?: string | null;
  email?: string | null;
  avatar_url?: string | null;
}

/**
 * Returns the resolved display name for a user.
 * Priority: full_name/name -> username -> email prefix -> "User"
 * Never returns "Google User".
 */
export function getUserDisplayName(user?: UserLike | null): string {
  if (!user) return "User";
  if (user.username && !user.username.toLowerCase().startsWith("user1")) {
    return user.username.trim();
  }
  const rawName = (user.name || user.full_name || user.username || "").trim();
  if (rawName && rawName.toLowerCase() !== "google user" && rawName.toLowerCase() !== "user") {
    return rawName;
  }
  if (user.email && user.email.includes("@")) {
    const prefix = user.email.split("@")[0];
    return prefix.charAt(0).toUpperCase() + prefix.slice(1);
  }
  return "User";
}

/**
 * Returns the user's first name (e.g., "Manikanta" from "Manikanta Gangiredla").
 */
export function getUserFirstName(user?: UserLike | null): string {
  const fullName = getUserDisplayName(user);
  const firstPart = fullName.split(" ")[0];
  return firstPart || "User";
}

/**
 * Generates avatar initials from display name or email.
 * Examples:
 * - "Manikanta Gangiredla" -> "MG"
 * - "John Doe" -> "JD"
 * - "manikanta@gmail.com" -> "M"
 */
export function getUserInitials(userOrName?: UserLike | string | null): string {
  let cleanName = "";

  if (typeof userOrName === "string") {
    cleanName = userOrName.trim();
  } else if (userOrName) {
    cleanName = getUserDisplayName(userOrName);
  }

  if (!cleanName || cleanName.toLowerCase() === "user" || cleanName.toLowerCase() === "google user") {
    if (typeof userOrName === "object" && userOrName?.email) {
      cleanName = userOrName.email.split("@")[0];
    } else {
      return "U";
    }
  }

  const parts = cleanName.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  if (parts.length === 1 && parts[0]) {
    return parts[0].substring(0, Math.min(2, parts[0].length)).toUpperCase();
  }
  return "U";
}
