"""The web app manifest and the app icons, built from the default company's logo (Company > Company Logo).

Served from the site root so the installed app can use them:
  /alsa-estimation-manifest.json
  /alsa-estimation-icon-192.png and /alsa-estimation-icon-512.png (the logo on white, inside the maskable safe zone)
Without a company logo, the icon is a plain sheet drawn in the app's colors."""

import io
import json

import frappe
from frappe.website.page_renderers.base_renderer import BaseRenderer
from werkzeug.wrappers import Response

from alsa_estimation import APP_ROUTE, APP_TITLE

MANIFEST = "alsa-estimation-manifest.json"
ICONS = {"alsa-estimation-icon-192.png": 192, "alsa-estimation-icon-512.png": 512}
INK = "#172033"
GROUND = "#F3F5F8"


def company_logo():
	company = frappe.defaults.get_global_default("company")
	logo = frappe.db.get_value("Company", company, "company_logo") if company else None
	return logo or frappe.db.get_value("Company", {"company_logo": ["is", "set"]}, "company_logo")


def manifest():
	route = f"/{APP_ROUTE}"
	icons = [
		{"src": f"/{path}", "sizes": f"{size}x{size}", "type": "image/png", "purpose": purpose}
		for path, size in ICONS.items()
		for purpose in ("any", "maskable")
	]
	return {
		"id": route,
		"name": APP_TITLE,
		"short_name": APP_TITLE,
		"start_url": route,
		"scope": route,
		"display": "standalone",
		"background_color": GROUND,
		"theme_color": INK,
		"icons": icons,
	}


def _png(image):
	buffer = io.BytesIO()
	image.save(buffer, "PNG", optimize=True)
	return buffer.getvalue()


def _logo():
	from PIL import Image

	url = company_logo()
	if not url:
		return None
	try:
		content = frappe.get_doc("File", {"file_url": url}).get_content()
		return Image.open(io.BytesIO(content)).convert("RGBA")
	except Exception:
		frappe.log_error(title="ALSA Estimation: could not read the company logo")
		return None


def _icon(size):
	from PIL import Image, ImageDraw

	logo = _logo()
	if logo is not None:
		logo.thumbnail((int(size * 0.72), int(size * 0.72)), Image.LANCZOS)
		canvas = Image.new("RGBA", (size, size), (255, 255, 255, 255))
		canvas.alpha_composite(logo, ((size - logo.width) // 2, (size - logo.height) // 2))
		return _png(canvas.convert("RGB"))

	scale = size / 512
	canvas = Image.new("RGB", (size, size), INK)
	draw = ImageDraw.Draw(canvas)
	draw.rounded_rectangle(
		[156 * scale, 112 * scale, 356 * scale, 400 * scale], radius=24 * scale, fill="#FFFFFF"
	)
	for top, right in ((188, 316), (240, 316), (292, 276)):
		draw.rounded_rectangle(
			[196 * scale, top * scale, right * scale, (top + 16) * scale], radius=8 * scale, fill=INK
		)
	return _png(canvas)


def _cached(key, build):
	"""Cached per logo, so a new logo shows without a deploy."""
	cache_key = f"alsa_estimation_brand:{key}:{company_logo() or '-'}"
	data = frappe.cache.get_value(cache_key)
	if data is None:
		data = build()
		frappe.cache.set_value(cache_key, data, expires_in_sec=6 * 3600)
	return data


class BrandingRenderer(BaseRenderer):
	def can_render(self):
		path = self.path.strip("/")
		return path == MANIFEST or path in ICONS

	def render(self):
		path = self.path.strip("/")
		if path == MANIFEST:
			response = Response(json.dumps(manifest()), mimetype="application/manifest+json")
		else:
			response = Response(_cached(path, lambda: _icon(ICONS[path])), mimetype="image/png")
		response.headers["Cache-Control"] = "public, max-age=3600"
		return response
