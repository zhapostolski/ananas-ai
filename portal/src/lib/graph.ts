/**
 * Microsoft Graph API client using client_credentials flow.
 * Requires GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET in env.
 */

let _tokenCache: { token: string; expiresAt: number } | null = null;

export async function getGraphToken(): Promise<string | null> {
  if (_tokenCache && Date.now() < _tokenCache.expiresAt - 60_000) {
    return _tokenCache.token;
  }

  const tenantId = process.env.GRAPH_TENANT_ID;
  const clientId = process.env.GRAPH_CLIENT_ID;
  const clientSecret = process.env.GRAPH_CLIENT_SECRET;

  if (!tenantId || !clientId || !clientSecret) return null;

  const res = await fetch(
    `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/token`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "client_credentials",
        client_id: clientId,
        client_secret: clientSecret,
        scope: "https://graph.microsoft.com/.default",
      }).toString(),
    }
  );

  if (!res.ok) return null;
  const data = await res.json() as { access_token?: string; expires_in?: number };
  if (!data.access_token) return null;

  _tokenCache = {
    token: data.access_token,
    expiresAt: Date.now() + (data.expires_in ?? 3600) * 1000,
  };

  return _tokenCache.token;
}

export interface GraphUser {
  id: string;
  displayName: string | null;
  mail: string | null;
  userPrincipalName: string;
  jobTitle: string | null;
  department: string | null;
  mobilePhone: string | null;
  officeLocation: string | null;
  accountEnabled: boolean;
}

/**
 * Fetch all users in the organisation from Microsoft Graph.
 * Requires User.Read.All application permission.
 */
export async function getOrgUsers(): Promise<GraphUser[]> {
  const token = await getGraphToken();
  if (!token) return [];

  const select = "id,displayName,mail,userPrincipalName,jobTitle,department,mobilePhone,officeLocation,accountEnabled";
  const users: GraphUser[] = [];
  let url: string | null = `https://graph.microsoft.com/v1.0/users?$select=${select}&$top=999&$filter=accountEnabled eq true`;

  while (url) {
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) break;
    const data = await res.json() as { value: GraphUser[]; "@odata.nextLink"?: string };
    users.push(...data.value);
    url = data["@odata.nextLink"] ?? null;
  }

  return users;
}

/**
 * Fetch profile photo for a user by their Azure object ID or UPN.
 * Returns base64 data URL or null.
 */
export async function getUserPhoto(userIdOrUpn: string): Promise<string | null> {
  const token = await getGraphToken();
  if (!token) return null;

  try {
    const res = await fetch(
      `https://graph.microsoft.com/v1.0/users/${encodeURIComponent(userIdOrUpn)}/photo/$value`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    if (!res.ok) return null;
    const buffer = await res.arrayBuffer();
    const base64 = Buffer.from(buffer).toString("base64");
    const contentType = res.headers.get("content-type") ?? "image/jpeg";
    return `data:${contentType};base64,${base64}`;
  } catch {
    return null;
  }
}
