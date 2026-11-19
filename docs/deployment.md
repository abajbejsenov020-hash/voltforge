# Deploy VOLTMODD

The Node service runs the API and serves the built frontend on the same HTTPS origin. Supabase provides email/password accounts and Postgres storage for each private garage.

## Supabase project

1. Create a dedicated project and apply the migration in `supabase/migrations`. The migration gives each signed-in account access to its own builds. Local SQLite stays available for development.
2. Set the Auth Site URL to the hosted HTTPS origin. Add `/api/auth/callback/confirm` and `/api/auth/callback/reset` on that same origin to the Redirect URLs list. [Supabase redirect settings](https://supabase.com/docs/guides/auth/redirect-urls)
3. Enable email confirmation. Configure a transactional SMTP sender in Supabase Auth for public confirmation and recovery mail. Open sign-up and reset links in the browser that requested them so the server can verify the browser's PKCE challenge. [Supabase SMTP setup](https://supabase.com/docs/guides/auth/auth-smtp) · [Supabase PKCE flow](https://supabase.com/docs/guides/auth/sessions/pkce-flow)
4. Use the project URL and publishable key for the application. The server uses the signed-in user's token for database access.

## Render service

Use the repository’s `render.yaml` Blueprint to create the web service. Provide `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` in Render. The service uses Node 24, binds to the assigned port on all interfaces, and takes its public origin from `RENDER_EXTERNAL_URL`. Render checks `/api/health` before routing traffic. [Render Blueprint specification](https://render.com/docs/blueprint-spec)

## Railway service

Deploy the repository root using `railway.json`. Use Node 24 or newer and generate a public HTTPS domain. Set these variables on the service.

| Variable                   | Value                                                                 |
| -------------------------- | --------------------------------------------------------------------- |
| `HOST`                     | `0.0.0.0`                                                             |
| `APP_ORIGIN`               | The exact HTTPS origin, for example `https://voltmodd.up.railway.app` |
| `SUPABASE_URL`             | The Supabase project's API origin                                     |
| `SUPABASE_PUBLISHABLE_KEY` | The project's publishable key                                         |

Railway supplies `PORT` and checks `/api/health`. The build command prepares the frontend and the start command serves it through the Node app. [Railway Config as Code](https://docs.railway.com/config-as-code/reference)

## Verify the release

- Open the hosted configurator and load a vehicle model and a 3D setting.
- Create a test account, follow the confirmation link, sign in, and save a build. Sign in from a second browser and confirm the build is present.
- Use a second account and confirm its garage opens independently. Confirm guest drafts move only through **Import local builds** and remain available on the original device.
- For drafts from the local development URL, open **Your garage**, download the builds file, and import that file from the account dialog on the hosted site.
- Sign out and complete password recovery from the browser that requested the link.
