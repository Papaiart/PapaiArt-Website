"""
Static site generator for papaiart.com.

    python tools/sync_itch.py   # optional: pull new devlog posts from itch.io
    python build_site.py        # regenerate all pages

Generates index.html, software/*.html, devlog.html, devlog/*.html, about.html,
404.html, beta.html (redirect) and sitemap.xml, and refreshes the shared nav and
footer on the legacy Animation Studio pages (features, learn, cikkek/*).
Product copy lives in PRODUCTS below; devlog posts come from data/devlogs.json.
"""
import html
import json
import os
import re
from datetime import date, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://www.papaiart.com'
ITCH = 'https://papaiart.itch.io'
DISCORD = 'https://discord.gg/ecC59ZpbQ3'
PATREON = 'https://patreon.com/PapaiArt'
LINKEDIN = 'https://www.linkedin.com/in/bence-papai-papaiart/'
EMAIL = 'babharkft@gmail.com'
THREE_VERSION = '0.160.0'
TODAY = date.today()

e = html.escape


# ======================================================================
# Product data
# ======================================================================

PRODUCTS = [
    {
        'id': 'fps-lab',
        'name': 'FPS Lab',
        'full': 'PapaiArt Tools – FPS Lab',
        'itch': f'{ITCH}/papaiart-tools-fps-lab',
        'group': 'gamedev',
        'color': '#34c47e', 'ink': '#03140b',
        'hero': 'fps', 'shift': 0.2,
        'kicker': 'Game engine',
        'tagline': 'A free game engine for first-person games. Build by connecting nodes, not by writing code.',
        'card': 'Visual-scripting game engine for first-person games. Scene, logic, UI and a one-click Windows build.',
        'lead': 'Assemble a scene, wire up behaviour with visual scripting, press Play, and export a standalone Windows game. Native Vulkan, fast startup, no project import step.',
        'status': 'In development',
        'price': 'Free', 'price_note': 'Pay what you want',
        'platforms': 'Windows',
        'hero_shot': 'shot-01.webp',
        'overview': [
            'FPS Lab is a game engine where you build the game by connecting visual nodes instead of writing code. The player controller, the weapon handling and most of the built-in tooling are built for first-person games. The scene, scripting, UI and build systems are general, so third-person games, walking sims and puzzle games work too.',
            'It\'s aimed mostly at people making their first game. Everything happens in one editor window with a few tabs. A beginner handbook starts from an empty scene and works up to a zombie shooter and a horror game. The first project, a room you can walk around in, takes about ten minutes.',
            'The engine is free, with no paid unlock, no watermark on your builds and no revenue share. What you make is yours: an exported game is a standalone program with no engine, launcher or licence check behind it. Development is funded by the community.',
        ],
        'callout': ('Who it\'s for', [
            'First-time game makers: a handbook takes you from zero to a finished shooter',
            'Retro and modern first-person shooters',
            'Walking sims, horror and puzzle games',
            'Experienced devs who want a fast, native editor',
        ]),
        'features': [
            ('Scene and objects', 'Build your level from a hierarchy of objects, bring in your own models, and pull in finished maps from the other PapaiArt tools.', [
                'Move, rotate and edit several objects at once',
                '<strong>FBX and glTF/GLB</strong> import, skeletons and animations included',
                'Prefabs you can place in the editor or spawn while the game runs',
                'Import finished levels from <strong>Level Modeller</strong> with baked lighting, or a <strong>Level Editor</strong> map',
                'New objects appear where you are looking, not at the world origin',
            ], 'shot-03.webp'),
            ('Visual scripting', 'Events, flow, variables, arrays and globals: enough for pickups, an inventory, enemy AI and keeping score.', [
                'A player who walks, collides with walls and sets off triggers',
                'Raycast shooting and collision layers that decide what hits what',
                '<strong>Jolt</strong> rigid-body physics for things that fall, roll and get pushed',
                'Sound placed in 3D space, with mixer buses for music and effects',
                'Name your controls once in the Input Manager and rebinding becomes a settings screen',
            ], 'shot-08.webp'),
            ('Enemies that find their own way', 'Place a Nav Volume, press Bake, and a Nav Agent walks (or flies) to wherever you send it.', [
                'Around walls, up stairs, off ledges and around the other agents',
                'Chase, patrol, stop, "could it even reach me from there?", all from script nodes',
                'The floor the AI can actually use is drawn in the editor, so you see what it sees',
                'A voxel field instead of a navmesh, so flying enemies need no extra setup',
            ], 'shot-09.webp'),
            ('How it looks', 'Shared PBR materials, node-built material effects and screen effects you can see live in the editor.', [
                'Build material effects by connecting nodes, with a live preview and no shader code',
                'Lights, shadows and baked lighting; mipmapping and anisotropic filtering',
                'Fog, vignette, VHS and other screen effects, live in the editor, not only in play',
                'Classic 2D sprite enemies with eight viewing angles from a single image sheet',
                'Particles, 3D text and level of detail that never changes collision',
            ], 'shot-06.webp'),
            ('Animation that doesn\'t snap', 'Keyframe anything on a timeline, cut long takes into clips and blend between them.', [
                '<strong>Blend</strong> input on Play Animation, so a weapon or a door never pops between poses',
                '<strong>On Animation End</strong> event: no more polling every frame',
                'Frame events: a footstep on the frame the boot lands, a muzzle flash on the exact frame',
                'A weapon held in view that sways and bobs as you move',
            ], 'shot-01.webp'),
            ('Turning it into a game', 'Menus, scene flow and a single build step that produces a real Windows program.', [
                'On-screen UI: health bar, score, pause screen and a settings menu that works',
                'Chain your scenes together with the <strong>Game Flow</strong> graph',
                'Game-wide settings for collision layers, controls and frame rate',
                'One build step produces a standalone <strong>.exe</strong> that runs without FPS Lab',
            ], 'shot-05.webp'),
        ],
        'cards_title': 'What\'s next',
        'cards': [
            ('Linux & macOS export', 'Builds for more platforms are next on the list.'),
            ('More script nodes', 'New nodes, prioritised by what people ask for.'),
            ('More handbook', 'More chapters and example projects for beginners.'),
        ],
        'videos': [('V1Sor9d_8Ys', 'FPS Lab trailer')],
        'requirements': ['Windows 10 or newer, 64-bit', 'A GPU with Vulkan support', 'No installer and no account: unzip and run'],
        'support': True,
    },
    {
        'id': 'level-editor',
        'name': 'Level Editor',
        'full': 'PapaiArt Tools – Level Editor',
        'itch': f'{ITCH}/papaiart-tools-level-editor',
        'group': 'gamedev',
        'color': '#ffc800', 'ink': '#161100',
        'hero': 'editor', 'shift': 0.2,
        'kicker': 'Doom-style level editor',
        'tagline': 'Draw a room. Walk through it. Ship it to Unity, Godot, TrenchBroom or EasyFPSEditor.',
        'card': 'Doom-style sector editor: sketch in 2D, walk in 3D, export to Unity, Quake .map, EFPSE, OBJ and GLB.',
        'lead': 'The classic sketch-first sector workflow. Draw polygons on a 2D grid, push floors and ceilings around, drop in a player start, and you are already walking through the level.',
        'status': 'Released',
        'price': '$20', 'price_note': 'One-time purchase',
        'platforms': 'Windows',
        'hero_shot': 'shot-02.webp',
        'overview': [
            'Level Editor is built around the classic Doom sector workflow, the fast, sketch-first approach behind some of the most memorable shooters ever made. Draw polygons on a 2D grid, set floor and ceiling heights, textures and light, then press Tab to walk through it in first person.',
            'When the map is ready, it goes wherever your project lives: a one-drop Unity package, OBJ and GLB, a Valve 220 Quake .map for TrenchBroom and Godot, or straight into an EasyFPSEditor project. Version 2.0 adds sector light and colour, upper and lower wall textures, free-standing walls and Doom WAD import.',
            'It\'s made for indie developers, modders, hobbyists, students and weekend tinkerers, anyone who wants to work on the shape of a space instead of on their tools.',
        ],
        'callout': ('Perfect for', [
            'Rapid prototyping: sketch, walk and play the same afternoon',
            'Retro FPS games with Doom/Quake-style architecture',
            'Mod development and custom levels',
            'Teaching level design and 3D geometry',
        ]),
        'features': [
            ('Sketch in 2D', 'Click to drop vertices or drag out whole shapes. Sectors snap, nest and split the way you expect.', [
                'Sector drawing with vertex snapping, plus drag-to-draw rectangle, ellipse, star and <strong>stairs</strong>',
                'Nested sectors: pedestals, pillars and holes with real portal walls',
                'Drawing over a sector splits it cleanly (robust Clipper2 polygon clipping)',
                'Marquee selection with a scale/rotate gizmo; duplicates float until you place them',
                'Floor textures shown faintly in the 2D plan view, aligned exactly like in 3D',
            ], 'shot-01.webp'),
            ('Walk it in 3D', 'Real-time first-person preview with portal rendering and collision, and texturing without leaving the view.', [
                'Shift-click to select many faces and texture them in one click',
                '<strong>Sector brightness and colour</strong>: tint rooms without duplicating materials',
                'Upper and lower wall textures for lintels, window bands and trim',
                'Wall and floor Tile Mode, UV sliding with the arrow keys',
                'Exponential fog and a full 3D view settings dialog with key rebinding',
            ], 'shot-02.webp'),
            ('Ship it to Unity', 'Export the bundle, drag the folder into Assets/, and you have a ready-to-play prefab.', [
                'Self-contained bundle: .pamap map, texture sidecar and only the textures you used',
                'Auto-generated MaterialDatabase: no missing-pink surfaces, no manual wiring',
                'Correct world scale, mesh colliders and Thing spawns on the first import',
                'Live reimport, override hooks for your own PBR materials',
                'URP-ready (Unity 2021.3+), Standard fallback, and a shader for sector light',
            ], 'shot-05.webp'),
            ('Quake .map and EasyFPSEditor', 'Draw rooms once and open them in whichever brush-based tool or engine comes next.', [
                '<strong>Valve 220 .map</strong> for TrenchBroom, J.A.C.K., NetRadiant, func_godot, Scopa, Unreal and Blender',
                'Leak-free brushes, merged convex pieces, real slopes, textures copied alongside',
                '<strong>EasyFPSEditor</strong> export with custom blocks for off-grid walls and true ramps',
                'Every export runs as a dry-run preview first, and writes are atomic with a .bak backup',
                'Open <strong>Doom WADs</strong>: levels arrive as real, editable geometry with textures',
            ], 'shot-11.webp'),
        ],
        'cards_title': 'Export formats',
        'cards': [
            ('Unity bundle', 'One-drop .pamap import with materials, colliders and spawns.'),
            ('Quake .map', 'Valve 220 for TrenchBroom, Godot, Unreal, Blender.'),
            ('EasyFPSEditor', 'Writes .eem maps straight into an existing project.'),
            ('OBJ / MTL', 'With pivot, scale and optional texture copy.'),
            ('glTF 2.0 (GLB)', 'Binary glTF with materials, vertex light tint included.'),
            ('Doom WAD import', 'Bring classic levels in as editable geometry.'),
        ],
        'videos': [
            ('3kwfcRsGEoo', 'Level Editor 2.0'),
            ('dYZutuwFg6I', 'Version 1.6.2 features'),
            ('AJik_4h2qSA', 'Version 1.4.4: multi-select in 3D'),
            ('Jgn5xIBLaNo', 'Version 1.4.3 features'),
            ('xrR8dY3guTU', 'Feature walkthrough'),
        ],
        'requirements': ['Windows 10 / 11', 'Unity 2021.3 or newer for the optional Unity package', 'PDF user guides included (English and Hungarian)'],
    },
    {
        'id': 'level-modeller',
        'name': 'Level Modeller',
        'full': 'PapaiArt Tools – Level Modeller',
        'itch': f'{ITCH}/papaiart-tools-level-modeller',
        'group': 'gamedev',
        'color': '#a594ff', 'ink': '#0e0a1f',
        'hero': 'modeller', 'shift': 0.2,
        'kicker': 'CSG level editor',
        'tagline': 'CSG level design with GPU light baking. Block out, carve, texture, bake and export.',
        'card': 'Standalone CSG level editor with live booleans, per-face texturing, GPU lightmap baking and clean exports.',
        'lead': 'Build levels from primitives and boolean operations the way Quake-era editors did, with a Vulkan renderer, automatic lightmap UVs and a clean mesh at the end.',
        'status': 'Released',
        'price': '$20', 'price_note': 'One-time purchase',
        'platforms': 'Windows',
        'hero_shot': 'shot-03.webp',
        'overview': [
            'Level Modeller is a standalone CSG level editor. Additive shapes add volume, and subtractive shapes cut doorways, windows and corridors out of it. It\'s the workflow of TrenchBroom or ProBuilder, as a dedicated tool with a Vulkan renderer. Every shape stays a live object in the hierarchy: move it later and the booleans re-evaluate in real time.',
            'Texture with box-projected UVs from a project-wide library, place lights, and bake. The tool generates the lightmap UV channel itself (xatlas) and bakes on the GPU, so there is no manual unwrapping. Export to OBJ, GLB or a Unity bundle and go straight into Unity, Unreal or Godot.',
            'The boolean output goes through a cleanup pass that merges coplanar faces and retriangulates them, so what you export is a clean mesh, not triangle soup. Projects are a single JSON .lmmap file, easy to back up and easy to put in git.',
        ],
        'callout': ('Details that matter', [
            'Real-time booleans on a live object hierarchy',
            'GPU lightmap baking with multi-page atlases',
            'Level Editor maps import as real meshes',
            'Blender-style controls: Q / W / E / R',
            'Prefabs reusable across projects',
        ]),
        'features': [
            ('Block out with live booleans', 'Primitives, positive and negative shapes, and a hierarchy that re-evaluates as you work.', [
                'Box, cylinder, sphere, staircase, terrain and spline primitives',
                'Flip an object inside-out and a single box becomes a finished room',
                'Box select, group move and Ctrl+D duplicate of whole rooms',
                '<strong>Snapping</strong> to the grid, corners, edges, surfaces, pivots and bounds',
                'A CSG core that handles thousands of polygons without freezing',
            ], 'shot-02.webp'),
            ('Texture every face', 'A project-wide texture library, box-projected UVs, and per-face control when you need it.', [
                'Face Select mode: its own texture, scale and UV transform per face',
                'Cut surfaces keep their textures through booleans',
                'Import OBJ meshes as first-class primitives, with their own UVs or ours',
                'Multi-material objects',
            ], 'shot-10.webp'),
            ('Bake the light', 'Place point, spot and directional lights and hit Bake. The unwrap happens by itself.', [
                'Automatic lightmap UVs (xatlas) in an atlas that grows in pages to keep texel density',
                '<strong>GPU bake</strong> in a compute shader, with a silent CPU fallback',
                'Per-object lightmap density and honest bake statistics',
                'Indirect-only mode for games that light themselves in realtime',
            ], 'shot-12.webp'),
            ('Shapes boxes can\'t make', 'Curves, spirals and ground, all of which still take part in the booleans.', [
                '<strong>Spline Mesh</strong>: sweep a profile along Poly, Bezier or Catmull-Rom curves',
                'Spiral staircases with a centre pole and open risers',
                'Terrain objects with a height brush and four paint layers; carve caves into them',
                'A profile editor with zoom, pan, multi-select and a transform box',
            ], 'shot-08.webp'),
            ('Walk it, then ship it', 'Playtest in first person with the character your game will use, then export.', [
                'Walk Mode with collision, jumping, step-up and a configurable FPS avatar',
                'OBJ + MTL, or GLB with two UV channels and embedded or external textures',
                'Optional single-atlas export with the lightmap multiplied in',
                'Unity package with multi-page lightmaps; levels also open in <strong>FPS Lab</strong>',
            ], 'shot-11.webp'),
        ],
        'videos': [('SXYM_jGtDL4', 'Level Modeller trailer'), ('WLpI8_h8byA', 'Feature walkthrough')],
        'requirements': ['Windows 10 / 11, 64-bit', 'A GPU with Vulkan support'],
    },
    {
        'id': 'terrain-generator',
        'name': 'Terrain Generator',
        'full': 'PapaiArt Tools – Terrain Generator',
        'itch': f'{ITCH}/papaiart-tools-terrain-generator',
        'group': 'gamedev',
        'color': '#eaa640', 'ink': '#1a1004',
        'hero': 'terrain', 'shift': 0.22,
        'kicker': 'Landscape generator',
        'tagline': 'Build eroded landscapes, walk around in them, and export heightmaps, meshes, skies and print-and-play maps.',
        'card': 'Noise, erosion and a node graph for landscapes. Walk them in 3D, then export maps, meshes, skies or board-game sheets.',
        'lead': 'Start from noise and erosion, shape the result by hand, look at it as a full 3D world with sky, sea and weather, then export something your engine, renderer or printer can use.',
        'status': 'New release',
        'price': '$15', 'price_note': 'One-time purchase',
        'platforms': 'Windows',
        'hero_shot': 'shot-01.webp',
        'overview': [
            'Terrain Generator is a standalone desktop tool for building landscapes. It starts with a fractal base with ridged crests, then runs a water simulation that cuts real drainage into it. Thermal erosion, river incision, terracing and domain warp are separate steps you can reorder.',
            'When the sliders aren\'t enough, there is a node graph with Voronoi cells, fault scarps, fold ranges, impact craters, mesas, karst towers, volcanoes, and blend, mask and remap nodes. About 45 presets cover mountains, coasts, deserts, karst, plains and volcanic land.',
            'The viewport shows the finished look, not a proxy. Walk mode drops you into the landscape as a first-person avatar, so you can walk or swim across it.',
        ],
        'callout': ('Export targets', [
            'Heightmaps: PNG 8/16-bit, RAW r16 / r32, Radiance HDR',
            'Normal, AO, hillshade, rivers, contours, splat masks',
            'Meshes: OBJ, FBX, glTF/GLB, STL, PLY with LOD tiles',
            'Skies: HDRI panoramas, cube maps, engine skyboxes',
            'Print-and-play hex or square board maps',
        ]),
        'features': [
            ('Generate', 'Noise, erosion and landforms, each as its own step you can reorder.', [
                'Noise and <strong>droplet erosion</strong> that cuts real drainage',
                'Thermal erosion, river incision, terracing and domain warp',
                'A node graph for craters, mesas, karst towers, volcanoes, fault scarps and more',
                'Import a heightmap as a node and build on top of it',
                '~45 presets grouped by landscape type',
            ], 'shot-02.webp'),
            ('Shape it by hand', 'A non-destructive curve stack over the generated land.', [
                'Draw a line to flatten a road, raise a ridge or dig a trench',
                'Cut-only and fill-only modes, four falloff profiles, width and feather per curve',
                'Re-roll the terrain underneath and the curves still hold',
                'Worlds up to 8 × 8 sectors, 10 m to 20 km per sector edge',
            ], 'shot-01.webp'),
            ('See it before you export', 'The viewport is the final look, with sky, sea and weather.', [
                'Four authorable material layers with noise-broken transitions',
                'Sea with waves, foam, wet shorelines, caustics and an underwater look',
                'Volumetric clouds, cloud shadows, haze, sun shafts and ground mist',
                'Procedural grass, rocks and pebbles that thin out with distance',
                '<strong>Walk mode</strong>: walk or swim across the site in first person',
            ], 'shot-04.webp'),
            ('Export anywhere', 'Maps, meshes and skies, with ready-made presets for the big engines.', [
                'Presets for <strong>Unity, Unreal</strong> (Z-up, centimetres), <strong>Godot</strong> and <strong>Blender</strong>',
                'One mesh, one per sector, or streaming tiles with an LOD ladder and skirts',
                'Equirectangular panoramas, cube maps in five layouts, six-face skyboxes',
                'Up axis, handedness, scale and UV layout are all yours',
            ], 'shot-03.webp'),
            ('Tabletop maps', 'A full print-and-play board export for your next campaign.', [
                'Hex (pointy or flat top) or square grids',
                'A4, Letter, Tabloid and A2 multi-sheet layouts',
                'Coordinate labels, legend, compass, scale bar, elevation key and movement cost',
                'Fantasy-antique, blueprint, contour ink, cartographic or phosphor-terminal styles',
            ], 'shot-05.webp'),
        ],
        'videos': [('hi7Nh1JPMOo', 'Terrain Generator overview')],
        'requirements': ['Windows 10 / 11, 64-bit', 'A graphics card from roughly the last decade, up-to-date drivers', 'No installer, no dependencies, no account, no internet connection'],
    },
    {
        'id': 'animation-studio',
        'name': 'Animation Studio',
        'full': 'PapaiArt Animation Studio',
        'itch': f'{ITCH}/papaiart-animation-studio-open-beta',
        'group': 'art',
        'color': '#2ea4f5', 'ink': '#ffffff',
        'hero': 'animation', 'shift': 0.2,
        'kicker': 'Hybrid 2D/3D animation',
        'tagline': 'Hybrid 2D/3D animation: draw in 3D space, model, rig and render straight to MP4.',
        'card': 'Frame-by-frame drawing inside a real 3D scene, non-destructive modelling, IK rigging and MP4 export.',
        'lead': 'Built for the Spider-Verse look: frame-by-frame 2D drawing inside a real 3D scene, non-destructive modelling, IK rigging and one-click MP4 export, on a lightweight engine that starts in seconds.',
        'status': 'Open Beta',
        'price': 'Free', 'price_note': 'During the open beta',
        'platforms': 'Windows · macOS · Linux',
        'hero_shot': 'shot-05.webp',
        'overview': [
            'PapaiArt Animation Studio combines 2D and 3D animation in a new way. Think of the look of <em>Spider-Man: Across the Spider-Verse</em> or <em>Star Wars: Maul – Shadow Lord</em>, where hand-drawn lines live inside dimensional scenes. The program aims to become the dedicated tool for that style.',
            'The closed beta is over and the open beta is free for everyone. Version 1.0 was the first big milestone, with a new FBX pipeline, multi-material and multi-UV support and a GPU-buffer based renderer. The free period ends once all 1.5 features are ready.',
            'Made something cool with it? Send a screenshot or video that can be featured, and the Open Beta watermark will be removed for you. You also get a free key when the program launches on Steam.',
        ],
        'callout': ('Highlights', [
            '2D vector drawing inside the 3D viewport',
            'Non-destructive modelling with a modifier stack',
            'IK rigging and constraints',
            'FBX and OBJ import/export with presets',
            'Built-in H.264 MP4 export',
            'Blender-style G / R / S hotkeys',
        ]),
        'features': [
            ('Drawing in real 3D space', '2D drawings sit inside the 3D viewport, with cameras, depth and lighting. Vector strokes stay editable.', [
                'Drawing tracks and clips with exposure-sheet logic',
                'Onion skinning with customisable ink colours',
                'Pencil, Pen, Calligraphy and Rough brushes with pressure and tilt',
                'Independent stroke and fill for flat-design styles',
                'Drawing Layers: lines, shapes and images as separate sub-layers',
            ], 'shot-07.webp'),
            ('Non-destructive 3D modelling', 'A clean hierarchy and a real-time modifier stack, with the hotkeys Blender users already know.', [
                'Mirror and Subdivision Surface modifiers refresh instantly',
                'Interactive Bevel and Knife tools on the mesh',
                'Multi-material objects and multiple UV channels with a rewritten UV editor',
                'Modal <strong>G / R / S</strong> transforms with axis locks and typed values',
                'A pivot dot that shows exactly what you rotate and scale around',
            ], 'shot-08.webp'),
            ('Rigging and animation', 'Enough rigging to handle complex character animation, without leaving the program.', [
                'Inverse Kinematics, TrackTo, ChildOf and Limit constraints',
                'Timeline with keyframes, and infinite undo/redo',
                'Bone, skinning and animation export to FBX',
                'Dockable panels: Inspector, Viewport, Timeline, Hierarchy',
            ], 'shot-02.webp'),
            ('FBX pipeline and one-click render', 'Move assets in and out of other tools, and render the timeline without an external editor.', [
                'New FBX exporter with Blender-style presets: axes, scale, apply transform, triangulation',
                'Diffuse, normal and emissive maps, PBR scalars and per-face multi-material',
                'Texture path modes: absolute, relative, strip, or copy next to the FBX',
                'Built-in <strong>H.264 MP4</strong> and PNG sequence export at FHD or custom resolutions',
            ], 'shot-06.webp'),
        ],
        'links': [('features.html', 'Full capability list'), ('learn.html', 'Articles & tutorials')],
        'videos': [('Ne7pDUHR164', 'Animation Studio open beta')],
        'requirements': ['Windows 10 / 11, macOS or Linux', 'A GPU with up-to-date drivers', 'Tablet versions are planned'],
    },
    {
        'id': 'pixelpaint-98-pro',
        'name': 'PixelPaint 98 Pro',
        'full': 'PapaiArt PixelPaint 98 Pro',
        'itch': f'{ITCH}/papaiart-pixelpaint-98-pro',
        'group': 'art',
        'color': '#1fc1c1', 'ink': '#021717',
        'hero': 'pixelpaint', 'shift': 0,
        'kicker': 'Pixel art editor',
        'tagline': 'A pixel art editor with a full Python scripting layer underneath, and a proudly Windows 98 soul.',
        'card': 'Pixel art editor with a composable brush engine, sprite sheets and atlases, and a full Python API.',
        'lead': 'A tight, purpose-built pixel workflow with a custom brush engine, floating selections, sprite sheets and atlases, and a full Python API, so you can extend the app when the built-in tools aren\'t enough.',
        'status': 'Released',
        'price': 'Free', 'price_note': 'Pay what you want',
        'platforms': 'Windows',
        'hero_shot': 'shot-02.webp',
        'overview': [
            'PixelPaint 98 Pro is a professional pixel art editor built for artists who want precision, speed, and the freedom to shape their own tools.',
            'It combines a purpose-built pixel workflow with a full Python scripting layer. When the built-in tools aren\'t enough, you extend the app with your own tools, batch operations and export pipelines.',
            'It\'s built for professionals and technical artists who need a fast, reliable pixel editor every day, and the ability to automate or extend it when a project needs something the UI doesn\'t offer.',
        ],
        'callout': ('Who it\'s for', [
            'Pixel artists who want precision and speed',
            'Technical artists automating sprite pipelines',
            'Game devs exporting sheets and atlases',
            'Anyone who misses the Windows 98 look',
        ]),
        'features': [
            ('Core editing', 'A brush engine and selection tools designed for pixels.', [
                'Custom brush engine: tips and inks are separate, composable layers with stroke-wide opacity',
                'Non-destructive floating selections (move, scale, rotate) in a single undo step',
                'Multi-step tools with live preview: curve and polygonal lasso',
                'Tabbed documents, each with its own selection, history, zoom and active layer',
                'Snapshot-based undo/redo that also covers scripted operations',
            ], 'shot-02.webp'),
            ('Sprite sheets, animation and atlases', 'Import and export for game pipelines are built into the core, not added as plugins.', [
                'Native sprite sheet, animation sequence and texture atlas import/export',
                'No lock-in: your existing sheet and atlas conventions are supported directly',
            ], 'shot-01.webp'),
            ('Python scripting and addons', 'A real API over the document model, with its own bundled runtime.', [
                'Full <strong>pybind11</strong> API: document, layers, selections and tools',
                'Bundled, standalone Python runtime, with no separate install needed',
                'Write custom tools, batch operations or export pipelines as addons',
                'Built-in example addons to learn the API from',
                'Undo-safe: every scripted change can be rolled back like a manual edit',
            ], 'shot-05.webp'),
        ],
        'videos': [],
        'requirements': ['Windows'],
        'support': True,
    },
]
BY_ID = {p['id']: p for p in PRODUCTS}
NUMBER_WORDS = {n: w for n, w in enumerate(['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten'])}
GROUPS = [('gamedev', 'Game development'), ('art', 'Art & animation')]


# ======================================================================
# Helpers
# ======================================================================

ICONS = {
    'discord': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.317 4.37a19.79 19.79 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.211.375-.445.865-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.618-1.25.077.077 0 0 0-.079-.037A19.74 19.74 0 0 0 3.677 4.37a.07.07 0 0 0-.032.028C.533 9.046-.319 13.58.099 18.058a.082.082 0 0 0 .031.056 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.873-1.295 1.226-1.994a.076.076 0 0 0-.042-.106 13.1 13.1 0 0 1-1.872-.892.077.077 0 0 1-.008-.128c.126-.094.252-.192.372-.291a.074.074 0 0 1 .078-.011c3.928 1.793 8.18 1.793 12.061 0a.074.074 0 0 1 .079.01c.12.099.246.198.373.292a.077.077 0 0 1-.007.128 12.3 12.3 0 0 1-1.873.891.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.029 19.84 19.84 0 0 0 6.002-3.03.077.077 0 0 0 .032-.055c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.029zM8.02 15.331c-1.183 0-2.157-1.086-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.095 2.157 2.42 0 1.332-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.086-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.095 2.157 2.42 0 1.332-.946 2.418-2.157 2.418z"/></svg>',
    'arrow': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>',
    'download': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M7 10l5 5 5-5M4 21h16"/></svg>',
    'play': '<svg viewBox="0 0 24 24"><path d="M7 4.5v15l13-7.5z"/></svg>',
    'play-line': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M10 8.5v7l6-3.5z"/></svg>',
    'log': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16M4 12h10M4 19h13"/></svg>',
    'chat': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M9 11h.01M12 11h.01M15 11h.01"/></svg>',
    'heart': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 5.6a5.4 5.4 0 0 0-7.7 0L12 6.7l-1.1-1.1a5.4 5.4 0 0 0-7.7 7.7L12 22l8.8-8.7a5.4 5.4 0 0 0 0-7.7z"/></svg>',
    'store': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l1.5-5h15L21 9M3 9h18M3 9v11h18V9M9 20v-6h6v6"/></svg>',
    'mail': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
    'link': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>',
    'chev': '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>',
    'menu': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    'bolt': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg>',
    'box': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8l-9-5-9 5v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/></svg>',
    'layers': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/></svg>',
    'check': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5 9-10"/></svg>',
    'linkedin': '<svg viewBox="0 0 24 24"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM10 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05C21.6 8.65 22 11.3 22 14.1V21h-4v-6.1c0-1.46-.03-3.33-2.03-3.33-2.03 0-2.34 1.59-2.34 3.23V21h-4z"/></svg>',
}
CARD_ICONS = ['bolt', 'box', 'layers', 'check', 'arrow', 'log']


def slugify(s, n=60):
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
    return s[:n].rstrip('-') or 'post'


def fmt_date(d, short=False):
    dt = datetime.strptime(d, '%Y-%m-%d')
    return dt.strftime('%b %d, %Y' if short else '%B %d, %Y').replace(' 0', ' ')


def post_url(p):
    return f'devlog/{p["id"]}-{slugify(p["title"])}.html'


def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


def icon_src(pid, r):
    return f'{r}assets/images/icons/{pid}.png'


def shot(pid, name, r):
    return f'{r}assets/images/products/{pid}/{name}'


# ======================================================================
# Shared chrome
# ======================================================================

def nav(r, active=''):
    groups = ''
    for gid, label in GROUPS:
        groups += f'<div class="pa-mega__group">{e(label)}</div>'
        for p in PRODUCTS:
            if p['group'] != gid:
                continue
            groups += (f'<a href="{r}software/{p["id"]}.html"><img src="{icon_src(p["id"], r)}" alt="" width="38" height="38">'
                       f'<div><b>{e(p["name"])}</b><span>{e(p["kicker"])}</span></div></a>')
    act = lambda k: ' class="is-active"' if active == k else ''
    return f'''<nav class="pa-nav" aria-label="Main">
    <div class="pa-nav__inner">
        <a class="pa-brand" href="{r}index.html" aria-label="PapaiArt home">
            <img src="{r}assets/images/pa-mark.png" alt="" width="30" height="27">
            <span><b>PapaiArt</b><small>Software</small></span>
        </a>
        <button class="pa-nav__toggle" aria-label="Menu" aria-expanded="false">{ICONS['menu']}</button>
        <ul class="pa-menu">
            <li class="pa-has-mega"><button{act('software')} aria-haspopup="true">Software {ICONS['chev']}</button>
                <div class="pa-mega">{groups}</div>
            </li>
            <li><a href="{r}devlog.html"{act('devlog')}>Devlog</a></li>
            <li><a href="{r}about.html"{act('about')}>About</a></li>
            <li><a href="{ITCH}" target="_blank" rel="noopener">itch.io</a></li>
            <li class="pa-menu__mobile-cta"><a class="pa-btn pa-btn--primary" href="{DISCORD}" target="_blank" rel="noopener">{ICONS['discord']} Join the Discord</a></li>
        </ul>
        <a class="pa-btn pa-btn--primary pa-btn--sm pa-nav__cta" href="{DISCORD}" target="_blank" rel="noopener">{ICONS['discord']} Discord</a>
    </div>
</nav>'''


def footer(r):
    sw = lambda g: ''.join(f'<li><a href="{r}software/{p["id"]}.html">{e(p["name"])}</a></li>' for p in PRODUCTS if p['group'] == g)
    return f'''<footer class="pa-footer">
    <div class="pa-footer__grid">
        <div>
            <a class="pa-brand" href="{r}index.html"><img src="{r}assets/images/pa-mark.png" alt="" width="30" height="27"><span><b>PapaiArt</b><small>Software</small></span></a>
            <p>Independent creative software for animators, level designers and game developers. Built by Babhár Kft. in Hungary.</p>
            <div class="pa-footer__social">
                <a href="{DISCORD}" target="_blank" rel="noopener" aria-label="Discord">{ICONS['discord']}</a>
                <a href="{PATREON}" target="_blank" rel="noopener" aria-label="Patreon">{ICONS['heart']}</a>
                <a href="{ITCH}" target="_blank" rel="noopener" aria-label="itch.io">{ICONS['store']}</a>
                <a href="{LINKEDIN}" target="_blank" rel="noopener" aria-label="LinkedIn">{ICONS['linkedin']}</a>
            </div>
        </div>
        <div><h4>Game development</h4><ul>{sw('gamedev')}</ul></div>
        <div><h4>Art &amp; animation</h4><ul>{sw('art')}</ul></div>
        <div><h4>PapaiArt</h4><ul>
            <li><a href="{r}devlog.html">Devlog</a></li>
            <li><a href="{r}about.html">About</a></li>
            <li><a href="{r}about.html#contact">Contact</a></li>
            <li><a href="{r}learn.html">Animation Studio articles</a></li>
            <li><a href="{ITCH}" target="_blank" rel="noopener">All downloads on itch.io</a></li>
        </ul></div>
    </div>
    <div class="pa-footer__base">
        <span>© {TODAY.year} Babhár Kft. All rights reserved.</span>
        <span>Made in Hungary · <a href="mailto:{EMAIL}">{EMAIL}</a></span>
    </div>
</footer>'''


def head(r, title, desc, canonical, image=None, three=False, extra='', og_type='website', accent=None):
    image = image or f'{SITE}/assets/images/og/home.png'
    importmap = ''
    if three:
        importmap = f'''
    <script type="importmap">
    {{ "imports": {{
        "three": "https://cdn.jsdelivr.net/npm/three@{THREE_VERSION}/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@{THREE_VERSION}/examples/jsm/"
    }} }}
    </script>
    <link rel="modulepreload" href="https://cdn.jsdelivr.net/npm/three@{THREE_VERSION}/build/three.module.js" crossorigin>'''
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{e(title)}</title>
    <meta name="description" content="{e(desc)}">
    <meta name="author" content="Babhár Kft.">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <meta name="theme-color" content="{accent or '#0a0b10'}">
    <meta name="color-scheme" content="dark">
    <link rel="canonical" href="{canonical}">
    <meta property="og:type" content="{og_type}">
    <meta property="og:site_name" content="PapaiArt">
    <meta property="og:title" content="{e(title)}">
    <meta property="og:description" content="{e(desc)}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="{image}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{e(title)}">
    <meta name="twitter:description" content="{e(desc)}">
    <meta name="twitter:image" content="{image}">
    <link rel="icon" type="image/png" href="{r}assets/images/favicon.png">
    <link rel="apple-touch-icon" href="{r}assets/images/apple-touch-icon.png">
    <link rel="manifest" href="{r}site.webmanifest">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{r}assets/css/site.css">{importmap}
{extra}
</head>'''


def scripts(r, hero=False):
    s = f'\n<script src="{r}assets/js/site.js" defer></script>'
    if hero:
        s += f'\n<script type="module" src="{r}assets/js/heroes.js"></script>'
    return s + '\n</body>\n</html>\n'


def ld(obj):
    return f'    <script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'


# ======================================================================
# Components
# ======================================================================

def product_card(p, posts, r):
    latest = next((x for x in posts if x['product'] == p['id']), None)
    upd = f'Updated {fmt_date(latest["date"], True)}' if latest else p['platforms']
    ver = product_version(p, posts)
    badge = f'<span class="pa-chip pa-chip--accent"><span class="dot"></span>{e(p["status"])}{" · v" + ver if ver else ""}</span>'
    cover = p.get('card_shot', p['hero_shot'])
    return f'''<a class="pa-product reveal" href="{r}software/{p['id']}.html" style="--p:{p['color']};--p-ink:{p['ink']}">
    <div class="pa-product__top">
        <div class="pa-product__media"><img src="{shot(p['id'], cover, r)}" alt="{e(p['name'])} screenshot" loading="lazy" decoding="async"></div>
        <img class="pa-product__icon" src="{icon_src(p['id'], r)}" alt="" width="64" height="64">
        <div class="pa-product__badge">{badge}</div>
    </div>
    <div class="pa-product__body">
        <span class="pa-product__arrow">{ICONS['arrow']}</span>
        <h3>{e(p['name'])}</h3>
        <p>{e(p['card'])}</p>
        <div class="pa-product__meta"><span class="price">{e(p['price'])}</span><span class="upd">{e(upd)}</span></div>
    </div>
</a>'''


def post_card(p, r, show_product=True):
    prod = BY_ID[p['product']]
    img = (f'<div class="pa-post__media"><img src="{r}assets/images/devlog/{p["images"][0]["src"]}" alt="" loading="lazy" decoding="async"></div>'
           if p['images'] else
           f'<div class="pa-post__media pa-post__media--empty"><img src="{icon_src(prod["id"], r)}" alt=""></div>')
    tag = (f'<span class="pa-post__prod"><img src="{icon_src(prod["id"], r)}" alt="">{e(prod["name"])}</span>' if show_product else
           (f'<span class="pa-chip pa-chip--accent">v{e(p["version"])}</span>' if p['version'] else ''))
    return f'''<a class="pa-post reveal" href="{r}{post_url(p)}" data-product="{prod['id']}" style="--p:{prod['color']};--p-ink:{prod['ink']}">
    {img}
    <div class="pa-post__body">
        <div class="pa-post__top">{tag}<time class="pa-post__date" datetime="{p['date']}">{fmt_date(p['date'], True)}</time></div>
        <h3>{e(p['title'])}</h3>
        <p>{e(p['excerpt'])}</p>
    </div>
</a>'''


def video_block(vid, label, big=True):
    return (f'<div class="pa-video" data-yt="{vid}" data-title="{e(label)}"><button aria-label="Play video: {e(label)}"><span>{ICONS["play"]}</span></button>'
            f'<span class="pa-video__label">▶ {e(label)}</span></div>')


def product_version(p, posts):
    return next((x['version'] for x in posts if x['product'] == p['id'] and x['version']), p.get('version', ''))


# ======================================================================
# Pages
# ======================================================================

def build_home(posts):
    r = ''
    dock = ''.join(f'<a href="software/{p["id"]}.html"><img src="{icon_src(p["id"], r)}" alt="{e(p["name"])}" width="58" height="58"><span>{e(p["name"])}</span></a>' for p in PRODUCTS)
    groups = ''
    for gid, label in GROUPS:
        members = [p for p in PRODUCTS if p['group'] == gid]
        cards = ''.join(product_card(p, posts, r) for p in members)
        groups += f'<div class="pa-group-title reveal"><h3>{e(label)}</h3></div><div class="pa-products" style="--cols:{len(members)}">{cards}</div>'

    pipe_nodes = [
        ('level-editor', '01', 'Sketch the layout', 'Draw sectors in 2D, walk them in 3D. The fastest way from idea to playable space.', ['.pamap', 'Quake .map', 'EFPSE', 'WAD in']),
        ('level-modeller', '02', 'Carve & light it', 'Import the map as a mesh, carve it with booleans, texture every face and bake light on the GPU.', ['CSG', 'lightmaps', 'GLB', 'OBJ']),
        ('terrain-generator', '03', 'Grow the world', 'Eroded landscapes, skies and splat maps with presets for every major engine.', ['heightmaps', 'FBX', 'HDRI', 'splat']),
        ('fps-lab', '04', 'Make it a game', 'Bring levels in with baked lighting, script the gameplay with nodes, build a standalone .exe.', ['visual script', 'nav AI', '.exe']),
    ]
    pipe = ''
    for pid, n, title, text, io in pipe_nodes:
        p = BY_ID[pid]
        pipe += (f'<a class="pa-pipe__node reveal" href="software/{pid}.html" style="--p:{p["color"]}"><span class="pa-pipe__step">{n}</span>'
                 f'<img src="{icon_src(pid, r)}" alt="" width="48" height="48"><h3>{e(p["name"])}</h3><p><b style="color:#fff">{e(title)}.</b> {e(text)}</p>'
                 f'<div class="pa-pipe__io">{"".join(f"<span>{e(x)}</span>" for x in io)}</div></a>')

    latest = ''.join(post_card(p, r) for p in posts[:6])
    ld_org = {
        '@context': 'https://schema.org', '@type': 'Organization', '@id': f'{SITE}/#organization',
        'name': 'Babhár Kft.', 'alternateName': 'PapaiArt', 'url': f'{SITE}/',
        'logo': f'{SITE}/assets/images/company-logo.png', 'email': EMAIL,
        'founder': {'@type': 'Person', 'name': 'Bence Pápai', 'sameAs': LINKEDIN},
        'sameAs': [ITCH, DISCORD, PATREON, LINKEDIN],
    }
    ld_list = {
        '@context': 'https://schema.org', '@type': 'ItemList', 'name': 'PapaiArt software',
        'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f'{SITE}/software/{p["id"]}.html', 'name': p['full']} for i, p in enumerate(PRODUCTS)],
    }
    page = head(r, 'PapaiArt — Creative tools for building worlds',
                'Independent desktop software by PapaiArt: FPS Lab game engine, Doom-style Level Editor, CSG Level Modeller, Terrain Generator, Animation Studio and PixelPaint 98 Pro.',
                f'{SITE}/', three=True, extra=ld(ld_org) + '\n' + ld(ld_list))
    page += f'''
<body class="pa-dark">
{nav(r)}

<header class="pa-hero pa-hero--center hub-hero" data-hero="hub" style="--p:#5fb8f5">
    <div class="pa-wrap">
        <span class="pa-eyebrow">Independent creative software · Made in Hungary</span>
        <h1>Tools for<br><span class="grad">building worlds.</span></h1>
        <p class="hub-hero__lead">{NUMBER_WORDS[len(PRODUCTS)]} desktop tools for level designers, game developers and animators, each built from scratch on its own native engine. Sketch a level, carve it, grow a landscape around it, script it into a game, and animate whatever lives inside.</p>
        <div class="hub-hero__ctas">
            <a class="pa-btn pa-btn--primary pa-btn--lg" href="#software">Explore the software {ICONS['arrow']}</a>
            <a class="pa-btn pa-btn--ghost pa-btn--lg" href="devlog.html">{ICONS['log']} Read the devlog</a>
        </div>
        <nav class="pa-dock" aria-label="Products">{dock}</nav>
        <div class="pa-stats">
            <div><b>{len(PRODUCTS)}</b><span>desktop tools</span></div>
            <div><b>{len(posts)}</b><span>devlog posts</span></div>
            <div><b>{len({p['date'][:7] for p in posts})}</b><span>months of updates</span></div>
            <div><b>0</b><span>installers needed</span></div>
        </div>
    </div>
</header>

<section class="pa-section" id="software">
    <div class="pa-wrap">
        <div class="pa-head reveal">
            <span class="pa-eyebrow">The software</span>
            <h2>Small, fast, focused tools</h2>
            <p>Native C++ on Vulkan and OpenGL. No installer, no account, no launcher: unzip, run, and it starts in seconds.</p>
        </div>
        {groups}
    </div>
</section>

<section class="pa-section pa-section--alt">
    <div class="pa-wrap">
        <div class="pa-head reveal">
            <span class="pa-eyebrow">One pipeline</span>
            <h2>From a sketch on a grid to a game you can ship</h2>
            <p>The game-development tools are designed to hand work to each other. Level Editor maps import into Level Modeller as real meshes. FPS Lab loads both, baked lighting included. Everything also exports to the engine you already use.</p>
        </div>
        <div class="pa-pipe">{pipe}</div>
        <div class="pa-pipe__engines reveal"><b>Also exports to</b><span>Unity</span><span>Unreal</span><span>Godot</span><span>Blender</span><span>TrenchBroom</span><span>EasyFPSEditor</span></div>
    </div>
</section>

<section class="pa-section">
    <div class="pa-wrap">
        <div class="pa-head reveal" style="display:flex;justify-content:space-between;align-items:end;gap:24px;max-width:none;flex-wrap:wrap">
            <div style="max-width:640px"><span class="pa-eyebrow">Devlog</span><h2>Shipping every week</h2><p style="margin:0">Release notes and deep dives, straight from development.</p></div>
            <a class="pa-btn pa-btn--ghost" href="devlog.html">All {len(posts)} posts {ICONS['arrow']}</a>
        </div>
        <div class="pa-posts">{latest}</div>
    </div>
</section>

<section class="pa-section pa-section--alt">
    <div class="pa-wrap pa-maker">
        <div class="pa-maker__photo reveal"><img src="assets/images/creator_profil_picture.png" alt="Bence Pápai, founder and lead engine developer" width="220" height="220" loading="lazy"></div>
        <div class="reveal">
            <span class="pa-eyebrow">Built from scratch</span>
            <h2>One developer, his own engines</h2>
            <p style="font-size:1.1rem">PapaiArt is the software label of Bence Pápai and Babhár Kft. Every tool here runs on its own engine, written for real-time use. There are no heavyweight frameworks and no feature creep, just the features the job needs, built properly.</p>
            <div class="pa-principles">
                <div><b>Performance first</b><span>Instant startup, low memory, responsive on modest hardware.</span></div>
                <div><b>Yours to keep</b><span>No accounts, no DRM launchers, no revenue share on what you make.</span></div>
                <div><b>Built in the open</b><span>Weekly devlogs and a Discord where bug reports become features.</span></div>
            </div>
            <p style="margin-top:26px"><a class="pa-btn pa-btn--ghost" href="about.html">About PapaiArt {ICONS['arrow']}</a></p>
        </div>
    </div>
</section>

{community_section(r)}

{footer(r)}'''
    page += scripts(r, hero=True)
    write('index.html', page)


def community_section(r):
    return f'''<section class="pa-section">
    <div class="pa-wrap">
        <div class="pa-head pa-head--center reveal"><span class="pa-eyebrow">Community</span><h2>Build it with us</h2><p>Report a bug, request a node, show off a level. The last bug report turned into two new features.</p></div>
        <div class="pa-community">
            <a class="reveal" href="{DISCORD}" target="_blank" rel="noopener" style="--c:#5865f2">{ICONS['discord']}<h3>Discord</h3><p>Support, feature requests, work-in-progress screenshots and release announcements.</p><span>Join the server →</span></a>
            <a class="reveal" href="{PATREON}" target="_blank" rel="noopener" style="--c:#ff7a66">{ICONS['heart']}<h3>Patreon</h3><p>FPS Lab and PixelPaint are free. Community support pays for the next version.</p><span>Support development →</span></a>
            <a class="reveal" href="{ITCH}" target="_blank" rel="noopener" style="--c:#ff5c6e">{ICONS['store']}<h3>itch.io</h3><p>Every tool is downloaded from itch.io. Follow to get notified about new builds.</p><span>Visit the store →</span></a>
        </div>
    </div>
</section>'''


def build_product(p, posts):
    r = '../'
    mine = [x for x in posts if x['product'] == p['id']]
    ver = product_version(p, posts)
    style = f'--p:{p["color"]};--p-ink:{p["ink"]}'
    url = f'{SITE}/software/{p["id"]}.html'

    chips = [f'<span class="pa-chip pa-chip--accent"><span class="dot"></span>{e(p["status"])}</span>']
    if ver:
        chips.append(f'<span class="pa-chip">v{e(ver)}</span>')
    chips.append(f'<span class="pa-chip">{e(p["platforms"])}</span>')
    chips.append(f'<span class="pa-chip">{e(p["price"])} · {e(p["price_note"])}</span>')

    ctas = f'<a class="pa-btn pa-btn--primary pa-btn--lg" href="{p["itch"]}" target="_blank" rel="noopener">{ICONS["download"]} {"Download free" if p["price"] == "Free" else "Get it for " + e(p["price"])}</a>'
    if p['videos']:
        ctas += f'<a class="pa-btn pa-btn--ghost pa-btn--lg" href="#video">{ICONS["play-line"]} Watch video</a>'
    elif mine:
        ctas += f'<a class="pa-btn pa-btn--ghost pa-btn--lg" href="#devlog">{ICONS["log"]} Devlog</a>'

    hud = '<div class="fps-hud" aria-hidden="true"><i></i><i></i><i></i><i></i><b>PLAY</b></div>' if p['hero'] == 'fps' else ''
    hero_cls = 'pa-hero prod-hero'
    win_cls = 'pa-window'

    facts = [('Status', p['status']), ('Latest version', f'v{ver}' if ver else '—'), ('Platform', p['platforms']), ('Price', f'{p["price"]}'),
             ('Last update', fmt_date(mine[0]['date'], True) if mine else 'See itch.io')]
    facts_html = ''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in facts)

    overview = ''.join(f'<p>{x}</p>' for x in p['overview'])
    links = ''
    if p.get('links'):
        links = '<p style="display:flex;gap:12px;flex-wrap:wrap;margin-top:28px">' + ''.join(
            f'<a class="pa-btn pa-btn--ghost pa-btn--sm" href="{r}{href}">{e(label)} {ICONS["arrow"]}</a>' for href, label in p['links']) + '</p>'
    callout_title, callout_items = p['callout']
    callout = f'<aside class="pa-callout reveal"><h3>{e(callout_title)}</h3><ul>{"".join(f"<li>{e(x)}</li>" for x in callout_items)}</ul></aside>'

    features = ''
    for i, (title, lead, bullets, img) in enumerate(p['features']):
        flip = ' pa-feature--flip' if i % 2 else ''
        src = shot(p['id'], img, r)
        features += f'''<div class="pa-feature{flip}">
    <div class="pa-feature__copy reveal">
        <span class="pa-feature__num">{i + 1:02d} / {len(p['features']):02d}</span>
        <h3>{e(title)}</h3>
        <p class="pa-feature__lead">{e(lead)}</p>
        <ul>{"".join(f"<li>{b}</li>" for b in bullets)}</ul>
    </div>
    <div class="pa-feature__media reveal"><img src="{src}" data-zoom="{src}" data-group="features" alt="{e(p['name'])}: {e(title)}" loading="lazy" decoding="async"></div>
</div>'''

    cards = ''
    if p.get('cards'):
        items = ''.join(f'<div class="pa-card reveal"><div class="pa-card__ico">{ICONS[CARD_ICONS[i % len(CARD_ICONS)]]}</div><h3>{e(t)}</h3><p>{e(d)}</p></div>'
                        for i, (t, d) in enumerate(p['cards']))
        cards = f'''<section class="pa-section pa-section--tight pa-section--alt">
    <div class="pa-wrap"><div class="pa-head reveal"><span class="pa-eyebrow">{e(p['cards_title'])}</span></div><div class="pa-cards">{items}</div></div>
</section>'''

    video = ''
    if p['videos']:
        first, rest = p['videos'][0], p['videos'][1:]
        more = f'<div class="pa-videos">{"".join(video_block(v, l, False) for v, l in rest)}</div>' if rest else ''
        video = f'''<section class="pa-section" id="video">
    <div class="pa-wrap">
        <div class="pa-head pa-head--center reveal"><span class="pa-eyebrow">See it in action</span><h2>Watch {e(p['name'])}</h2></div>
        <div class="reveal">{video_block(*first)}</div>
        {more}
    </div>
</section>'''

    shots_dir = os.path.join(ROOT, 'assets', 'images', 'products', p['id'])
    shots = sorted(f for f in os.listdir(shots_dir) if f.startswith('shot-'))
    gallery = ''.join(f'<a href="{shot(p["id"], f, r)}" data-zoom="{shot(p["id"], f, r)}" data-group="gallery" class="reveal"><img src="{shot(p["id"], f, r)}" alt="{e(p["name"])} screenshot {i + 1}" loading="lazy" decoding="async"></a>'
                      for i, f in enumerate(shots))

    devlog = ''
    if mine:
        items = ''
        for x in mine[:8]:
            img = f'<img src="{r}assets/images/devlog/{x["images"][0]["src"]}" alt="" loading="lazy">' if x['images'] else f'<img src="{icon_src(p["id"], r)}" alt="" style="object-fit:contain;padding:18px">'
            v = f'<span class="pa-chip pa-chip--accent">v{e(x["version"])}</span>' if x['version'] else ''
            items += f'''<li class="reveal"><a href="{r}{post_url(x)}"><div class="pa-timeline__img">{img}</div><div>
    <div class="pa-timeline__meta">{v}<time datetime="{x['date']}">{fmt_date(x['date'])}</time></div>
    <h3>{e(x['title'])}</h3><p>{e(x['excerpt'])}</p></div></a></li>'''
        more = f'<p style="margin-top:10px"><a class="pa-btn pa-btn--ghost" href="{r}devlog.html?p={p["id"]}">All {len(mine)} {e(p["name"])} posts {ICONS["arrow"]}</a></p>' if len(mine) > 8 else ''
        devlog = f'''<section class="pa-section pa-section--alt" id="devlog">
    <div class="pa-wrap" style="max-width:980px">
        <div class="pa-head reveal"><span class="pa-eyebrow">Devlog</span><h2>Development timeline</h2><p>{len(mine)} updates since {fmt_date(mine[-1]['date'])}. Newest first.</p></div>
        <ol class="pa-timeline">{items}</ol>
        {more}
    </div>
</section>'''

    support = ''
    if p.get('support'):
        support = f'<a class="pa-btn pa-btn--ghost" href="{PATREON}" target="_blank" rel="noopener">{ICONS["heart"]} Support on Patreon</a>'
    cta = f'''<section class="pa-section">
    <div class="pa-wrap">
        <div class="pa-cta reveal">
            <img class="pa-cta__icon" src="{icon_src(p['id'], r)}" alt="">
            <div>
                <h2>{"Get " + e(p['name']) + " free" if p['price'] == 'Free' else "Get " + e(p['name'])}</h2>
                <p>{e(p['tagline'])}</p>
                <div class="pa-cta__meta">{"".join(f"<span>{e(x)}</span>" for x in p['requirements'])}</div>
            </div>
            <div class="pa-cta__actions">
                <a class="pa-btn pa-btn--primary pa-btn--lg" href="{p['itch']}" target="_blank" rel="noopener">{ICONS['download']} {"Download on itch.io" if p['price'] == 'Free' else e(p['price']) + " on itch.io"}</a>
                <a class="pa-btn pa-btn--ghost" href="{DISCORD}" target="_blank" rel="noopener">{ICONS['discord']} Ask on Discord</a>
                {support}
            </div>
        </div>
    </div>
</section>'''

    others = ''.join(f'<a href="{o["id"]}.html" style="--p:{o["color"]}"><img src="{icon_src(o["id"], r)}" alt=""><div><b>{e(o["name"])}</b><span>{e(o["kicker"])}</span></div></a>'
                     for o in PRODUCTS if o['id'] != p['id'])

    ld_app = {
        '@context': 'https://schema.org', '@type': 'SoftwareApplication', 'name': p['full'], 'url': url,
        'applicationCategory': 'MultimediaApplication' if p['group'] == 'art' else 'DeveloperApplication',
        'operatingSystem': p['platforms'].replace(' · ', ', '), 'description': p['lead'],
        'image': f'{SITE}/assets/images/products/{p["id"]}/{p["hero_shot"]}',
        'screenshot': [f'{SITE}/assets/images/products/{p["id"]}/{f}' for f in shots[:6]],
        'offers': {'@type': 'Offer', 'price': re.sub(r'[^0-9.]', '', p['price']) or '0', 'priceCurrency': 'USD', 'url': p['itch']},
        'publisher': {'@type': 'Organization', 'name': 'Babhár Kft.', 'url': f'{SITE}/'},
    }
    if ver:
        ld_app['softwareVersion'] = ver
    ld_crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f'{SITE}/'},
        {'@type': 'ListItem', 'position': 2, 'name': p['name'], 'item': url}]}

    page = head(r, f'{p["full"]} — {p["kicker"]}', p['lead'], url,
                image=f'{SITE}/assets/images/og/{p["id"]}.png',
                three=p['hero'] != 'pixelpaint', accent=p['color'],
                extra=ld(ld_app) + '\n' + ld(ld_crumbs))
    page += f'''
<body class="pa-dark" style="{style}">
{nav(r, 'software')}

<header class="{hero_cls}" data-hero="{p['hero']}" data-shift="{p['shift']}">
    {hud}
    <div class="pa-wrap prod-hero__grid">
        <div>
            <div class="prod-hero__id"><img src="{icon_src(p['id'], r)}" alt="" width="64" height="64"><span class="pa-eyebrow">{e(p['kicker'])}</span></div>
            <h1><small>{"PapaiArt Tools" if p['full'].startswith("PapaiArt Tools") else "PapaiArt"}</small>{e(p['name'])}</h1>
            <p class="prod-hero__tagline">{e(p['lead'])}</p>
            <div class="prod-hero__ctas">{ctas}</div>
            <div class="prod-hero__chips">{"".join(chips)}</div>
        </div>
    </div>
</header>

<div class="pa-wrap prod-showcase">
    <div class="{win_cls}">
        <div class="pa-window__bar"><i></i><i></i><i></i><span>{e(p['full'])}</span></div>
        <img src="{shot(p['id'], p['hero_shot'], r)}" data-zoom="{shot(p['id'], p['hero_shot'], r)}" alt="{e(p['name'])} interface" fetchpriority="high">
    </div>
    <dl class="pa-facts reveal">{facts_html}</dl>
</div>

<section class="pa-section">
    <div class="pa-wrap pa-overview">
        <div class="pa-overview__body reveal">
            <span class="pa-eyebrow">Overview</span>
            <h2>{e(p['tagline'])}</h2>
            {overview}
            {links}
        </div>
        {callout}
    </div>
</section>

<section class="pa-section pa-section--alt">
    <div class="pa-wrap">
        <div class="pa-head reveal"><span class="pa-eyebrow">Features</span><h2>What's inside</h2></div>
        {features}
    </div>
</section>

{cards}

{video}

<section class="pa-section{' pa-section--alt' if video else ''}">
    <div class="pa-wrap">
        <div class="pa-head reveal"><span class="pa-eyebrow">Gallery</span><h2>Screenshots</h2></div>
        <div class="pa-gallery">{gallery}</div>
    </div>
</section>

{devlog}

{cta}

<section class="pa-section pa-section--tight" style="padding-top:0">
    <div class="pa-wrap">
        <div class="pa-group-title"><h3>More from PapaiArt</h3></div>
        <div class="pa-more">{others}</div>
    </div>
</section>

{footer(r)}'''
    page += scripts(r, hero=True)
    write(f'software/{p["id"]}.html', page)


def build_devlog_index(posts):
    r = ''
    counts = {p['id']: sum(1 for x in posts if x['product'] == p['id']) for p in PRODUCTS}
    chips = f'<button class="pa-filter pa-filter--all is-active" data-filter="all">All <em>{len(posts)}</em></button>'
    chips += ''.join(f'<button class="pa-filter" data-filter="{p["id"]}" style="--p:{p["color"]}"><img src="{icon_src(p["id"], r)}" alt="">{e(p["name"])} <em>{counts[p["id"]]}</em></button>'
                     for p in PRODUCTS if counts[p['id']])
    body, month = '', None
    for x in posts:
        m = x['date'][:7]
        if m != month:
            if month:
                body += '</div>'
            month = m
            body += f'<h2 class="pa-month">{datetime.strptime(m, "%Y-%m").strftime("%B %Y")}</h2><div class="pa-posts">'
        body += post_card(x, r)
    body += '</div>'
    ld_blog = {'@context': 'https://schema.org', '@type': 'Blog', 'name': 'PapaiArt Devlog', 'url': f'{SITE}/devlog.html',
               'blogPost': [{'@type': 'BlogPosting', 'headline': x['title'], 'datePublished': x['date'], 'url': f'{SITE}/{post_url(x)}'} for x in posts[:20]]}
    page = head(r, 'Devlog — PapaiArt', 'Release notes and development deep dives for FPS Lab, Level Editor, Level Modeller, Animation Studio and the rest of the PapaiArt tools.',
                f'{SITE}/devlog.html', three=True, extra=ld(ld_blog))
    page += f'''
<body class="pa-dark">
{nav(r, 'devlog')}

<header class="pa-hero pa-hero--center hub-hero" data-hero="hub" style="--p:#5fb8f5;min-height:0;padding:130px 0 90px">
    <div class="pa-wrap">
        <span class="pa-eyebrow">Devlog</span>
        <h1>What's new<br><span class="grad">in the workshop.</span></h1>
        <p class="hub-hero__lead">{len(posts)} posts across {sum(1 for c in counts.values() if c)} tools: release notes, new features and the engineering behind them.</p>
    </div>
</header>

<section class="pa-section" style="padding-top:40px">
    <div class="pa-wrap">
        <div class="pa-filters" role="toolbar" aria-label="Filter by product">{chips}</div>
        {body}
    </div>
</section>

{community_section(r)}

{footer(r)}'''
    page += scripts(r, hero=True)
    write('devlog.html', page)


def build_post(x, prev_post, next_post):
    r = '../'
    p = BY_ID[x['product']]
    url = f'{SITE}/{post_url(x)}'
    cover = x['images'][0] if x['images'] else None
    bg = f'<div class="post-hero__bg" style="background-image:url({r}assets/images/devlog/{cover["src"]})"></div>' if cover else ''
    cover_html = ''
    if cover:
        src = f'{r}assets/images/devlog/{cover["src"]}'
        cover_html = f'<figure class="post-cover pa-wrap reveal"><img src="{src}" data-zoom="{src}" data-group="post" width="{cover["w"]}" height="{cover["h"]}" alt="{e(x["title"])}"></figure>'
    body = x['body'] or f'<p>{e(x["excerpt"])}</p>'
    if not x['body'].strip() or x['words'] < 5:
        body = f'<p>This update is mostly visual. See the screenshots below, and read the full post and comments on <a href="{x["url"]}" target="_blank" rel="noopener">itch.io</a>.</p>'
    gallery = ''
    if len(x['images']) > 1:
        gallery = '<div class="pa-wrap" style="max-width:1100px;margin-top:56px"><div class="pa-gallery">' + ''.join(
            f'<a href="{r}assets/images/devlog/{im["src"]}" data-zoom="{r}assets/images/devlog/{im["src"]}" data-group="post"><img src="{r}assets/images/devlog/{im["src"]}" alt="{e(x["title"])} screenshot {i + 2}" loading="lazy" decoding="async"></a>'
            for i, im in enumerate(x['images'][1:])) + '</div></div>'
    videos = ''
    if x['videos']:
        videos = '<div class="pa-wrap" style="max-width:900px;margin-top:48px">' + ''.join(video_block(v, x['title']) for v in x['videos']) + '</div>'
    nav_html = ''
    if prev_post or next_post:
        nav_html = '<div class="pa-wrap" style="margin-top:72px"><div class="post-nav">'
        if prev_post:
            nav_html += f'<a class="prev" href="{r}{post_url(prev_post)}"><small>← Older</small><b>{e(prev_post["title"])}</b></a>'
        if next_post:
            nav_html += f'<a class="next" href="{r}{post_url(next_post)}"><small>Newer →</small><b>{e(next_post["title"])}</b></a>'
        nav_html += '</div></div>'
    ver = f'<span class="pa-chip pa-chip--accent">v{e(x["version"])}</span>' if x['version'] else ''
    mins = max(1, round(x['words'] / 220))
    ld_post = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': x['title'], 'datePublished': x['date'], 'url': url,
               'author': {'@type': 'Person', 'name': 'Bence Pápai'}, 'publisher': {'@type': 'Organization', 'name': 'Babhár Kft.'},
               'about': {'@type': 'SoftwareApplication', 'name': p['full'], 'url': f'{SITE}/software/{p["id"]}.html'},
               'isBasedOn': x['url']}
    if cover:
        ld_post['image'] = f'{SITE}/assets/images/devlog/{cover["src"]}'
    page = head(r, f'{x["title"]} — {p["name"]} devlog', x['excerpt'][:200], url,
                image=f'{SITE}/assets/images/devlog/{cover["src"]}' if cover else None, og_type='article', accent=p['color'],
                extra=ld(ld_post) + f'\n    <link rel="alternate" href="{x["url"]}" title="Original post on itch.io">')
    page += f'''
<body class="pa-dark" style="--p:{p['color']};--p-ink:{p['ink']}">
{nav(r, 'devlog')}

<header class="post-hero">
    {bg}
    <div class="pa-wrap">
        <div class="post-crumb"><a href="{r}devlog.html">Devlog</a><span>/</span><a href="{r}software/{p['id']}.html">{e(p['name'])}</a></div>
        <h1>{e(x['title'])}</h1>
        <div class="post-hero__meta">
            <span class="pa-chip"><img src="{icon_src(p['id'], r)}" alt="" width="16" height="16" style="width:16px;height:16px">{e(p['name'])}</span>
            {ver}
            <span class="pa-chip"><time datetime="{x['date']}">{fmt_date(x['date'])}</time></span>
            <span class="pa-chip">{mins} min read</span>
        </div>
    </div>
</header>

{cover_html}

<article class="pa-wrap"><div class="pa-prose">{body}</div></article>
{videos}
{gallery}

<div class="pa-wrap" style="max-width:760px;margin-top:56px;display:flex;gap:12px;flex-wrap:wrap">
    <a class="pa-btn pa-btn--primary" href="{p['itch']}" target="_blank" rel="noopener">{ICONS['download']} Get {e(p['name'])}</a>
    <a class="pa-btn pa-btn--ghost" href="{x['url']}" target="_blank" rel="noopener">{ICONS['link']} Comment on itch.io</a>
    <a class="pa-btn pa-btn--ghost" href="{r}software/{p['id']}.html">{e(p['name'])} overview</a>
</div>
{nav_html}

<div style="height:100px"></div>
{footer(r)}'''
    page += scripts(r)
    write(post_url(x), page)


def build_about(posts):
    r = ''
    tools = ''.join(f'<a href="software/{p["id"]}.html" style="--p:{p["color"]}"><img src="{icon_src(p["id"], r)}" alt=""><div><b>{e(p["name"])}</b><span>{e(p["kicker"])}</span></div></a>' for p in PRODUCTS)
    qa = [
        ('What was the spark behind the first tool, PapaiArt Animation Studio?',
         'I felt there was a need for an animation program alongside Blender that supports the fusion of 2D and 3D animation, but as a much simpler program built specifically for that purpose. Perhaps the spark was seeing my university students struggle with learning so many overly complex programs just to realise their ideas.'),
        ('You build the engines from scratch. What was the hardest part?',
         'Designing the user interface. I had to translate a new concept into functional and intuitive layouts. What you see now evolved after a lot of redesigning and rethinking.'),
        ('Why include advanced features like IK in a lightweight package?',
         'Rigging and complex mechanics are essential parts of 3D animation. These features simply expand what users can do. I try to make professional tools as user-friendly as possible.'),
        ('What are you most excited to see people create?',
         'I built the canvas, but I can\'t wait to see the art: entirely new visual styles, true "2.5D" work where the line between hand-drawn and dynamic 3D blurs. The tools are ready; now it\'s up to the community\'s imagination.'),
    ]
    qa_html = ''.join(f'<h3>{e(q)}</h3><p>{e(a)}</p>' for q, a in qa)
    page = head(r, 'About — PapaiArt', 'PapaiArt is the software label of Bence Pápai and Babhár Kft., a Hungarian IT and publishing company building independent creative tools.',
                f'{SITE}/about.html', three=True)
    page += f'''
<body class="pa-dark">
{nav(r, 'about')}

<header class="pa-hero pa-hero--center hub-hero" data-hero="hub" style="--p:#5fb8f5;min-height:0;padding:130px 0 100px">
    <div class="pa-wrap">
        <span class="pa-eyebrow">About</span>
        <h1>Independent tools,<br><span class="grad">built from scratch.</span></h1>
        <p class="hub-hero__lead">PapaiArt is the software label of Babhár Kft., a Hungarian IT and publishing company, and its founder, engine developer Bence Pápai.</p>
    </div>
</header>

<section class="pa-section" style="padding-top:40px">
    <div class="pa-wrap pa-maker">
        <div class="pa-maker__photo reveal"><img src="assets/images/creator_profil_picture.png" alt="Bence Pápai" width="220" height="220"></div>
        <div class="reveal">
            <span class="pa-eyebrow">The maker</span>
            <h2>Bence Pápai</h2>
            <p style="font-size:1.1rem">Founder and lead engine developer. He started with PapaiArt Animation Studio after watching his university students struggle with heavyweight software. Since then, the lineup has grown into a family of game-development tools that hand work to each other, plus a pixel art editor with a Windows 98 soul.</p>
            <p style="display:flex;gap:12px;flex-wrap:wrap;margin-top:24px">
                <a class="pa-btn pa-btn--ghost" href="{LINKEDIN}" target="_blank" rel="noopener">{ICONS['linkedin'].replace('<svg', '<svg fill="currentColor"')} LinkedIn</a>
                <a class="pa-btn pa-btn--ghost" href="{ITCH}" target="_blank" rel="noopener">{ICONS['store']} itch.io</a>
            </p>
        </div>
    </div>
</section>

<section class="pa-section pa-section--alt">
    <div class="pa-wrap">
        <div class="pa-head reveal"><span class="pa-eyebrow">Principles</span><h2>What every tool has in common</h2></div>
        <div class="pa-cards">
            <div class="pa-card reveal"><div class="pa-card__ico">{ICONS['bolt']}</div><h3>Performance first</h3><p>Native engines written for real-time use. Everything starts in seconds and stays responsive on modest hardware.</p></div>
            <div class="pa-card reveal"><div class="pa-card__ico">{ICONS['box']}</div><h3>Focus over feature creep</h3><p>Fewer, well-built features instead of a thousand half-finished options.</p></div>
            <div class="pa-card reveal"><div class="pa-card__ico">{ICONS['check']}</div><h3>Yours to keep</h3><p>No installer, no account, no launcher. What you make with the tools belongs to you.</p></div>
            <div class="pa-card reveal"><div class="pa-card__ico">{ICONS['discord']}</div><h3>Built with the community</h3><p>{len(posts)} devlog posts so far. Bug reports and requests on Discord shape what gets built next.</p></div>
        </div>
    </div>
</section>

<section class="pa-section">
    <div class="pa-wrap" style="max-width:860px">
        <div class="pa-head reveal"><span class="pa-eyebrow">Behind the scenes</span><h2>Interview with the creator</h2></div>
        <div class="pa-prose reveal" style="margin:0">{qa_html}</div>
    </div>
</section>

<section class="pa-section pa-section--alt">
    <div class="pa-wrap">
        <div class="pa-head reveal"><span class="pa-eyebrow">The lineup</span><h2>{len(PRODUCTS)} tools and counting</h2></div>
        <div class="pa-more">{tools}</div>
    </div>
</section>

<section class="pa-section" id="contact">
    <div class="pa-wrap">
        <div class="pa-head pa-head--center reveal"><span class="pa-eyebrow">Contact</span><h2>Get in touch</h2><p>Bug reports, suggestions, press and partnerships. Every kind of feedback is welcome.</p></div>
        <div class="pa-community">
            <a class="reveal" href="mailto:{EMAIL}" style="--c:#5fb8f5">{ICONS['mail']}<h3>E-mail</h3><p>General questions, press, partnerships and bug reports.</p><span>{EMAIL}</span></a>
            <a class="reveal" href="{DISCORD}" target="_blank" rel="noopener" style="--c:#5865f2">{ICONS['discord']}<h3>Discord</h3><p>The fastest way to get help and talk to other users.</p><span>Join the server →</span></a>
            <a class="reveal" href="{PATREON}" target="_blank" rel="noopener" style="--c:#ff7a66">{ICONS['heart']}<h3>Patreon</h3><p>Help fund development of the free tools.</p><span>Support →</span></a>
        </div>
        <p class="reveal" style="text-align:center;margin-top:48px;color:var(--pa-dim);font-size:.9rem">Babhár Kft. · Hungary · <img src="assets/images/company-logo.png" alt="Babhár Kft. logo" style="display:inline-block;height:28px;width:auto;vertical-align:middle;filter:invert(1);opacity:.7;margin-left:6px"></p>
    </div>
</section>

{footer(r)}'''
    page += scripts(r, hero=True)
    write('about.html', page)


def build_404():
    r = '/'
    page = head(r, 'Page not found — PapaiArt', 'This page does not exist.', f'{SITE}/404.html', three=True)
    page = page.replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex">')
    page += f'''
<body class="pa-dark">
{nav(r)}
<header class="pa-hero pa-hero--center hub-hero" data-hero="hub" style="--p:#5fb8f5;min-height:78vh">
    <div class="pa-wrap">
        <span class="pa-eyebrow">Error 404</span>
        <h1>Nothing here<br><span class="grad">but wireframes.</span></h1>
        <p class="hub-hero__lead">The page you were looking for doesn't exist, or it moved when the site was rebuilt.</p>
        <div class="hub-hero__ctas"><a class="pa-btn pa-btn--primary pa-btn--lg" href="/">Back to home</a><a class="pa-btn pa-btn--ghost pa-btn--lg" href="/devlog.html">Read the devlog</a></div>
    </div>
</header>
{footer(r)}'''
    page += scripts(r, hero=True)
    write('404.html', page)


def build_beta_redirect():
    target = 'software/animation-studio.html'
    write('beta.html', f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PapaiArt Animation Studio — Open Beta</title>
    <meta name="robots" content="noindex">
    <link rel="canonical" href="{SITE}/{target}">
    <meta http-equiv="refresh" content="0; url={target}">
</head>
<body>
    <p>The open beta is live. <a href="{target}">Continue to PapaiArt Animation Studio</a>.</p>
</body>
</html>
''')


def refresh_legacy():
    """Swap the old nav/footer on the Animation Studio article pages for the shared chrome."""
    files = ['features.html', 'learn.html'] + [os.path.join('cikkek', f) for f in os.listdir(os.path.join(ROOT, 'cikkek')) if f.endswith('.html')]
    for rel in files:
        path = os.path.join(ROOT, rel)
        r = '../' if os.sep in rel or '/' in rel else ''
        s = open(path, encoding='utf-8').read()
        s = re.sub(r'<nav class="(?:site-nav|pa-nav)".*?</nav>', lambda m: nav(r, 'software'), s, count=1, flags=re.S)
        s = re.sub(r'<footer class="(?:site-footer|pa-footer)".*?</footer>', lambda m: footer(r), s, count=1, flags=re.S)
        if 'assets/css/site.css' not in s:
            s = re.sub(r'(<link rel="stylesheet" href="(?:\.\./)?assets/css/style\.css">)', lambda m: m.group(1) + f'\n    <link rel="stylesheet" href="{r}assets/css/site.css">\n    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">', s, count=1)
        if 'assets/js/site.js' not in s:
            s = s.replace('</body>', f'<script src="{r}assets/js/site.js" defer></script>\n</body>', 1)
        s = s.replace('<script type="module" src="assets/js/hero-effect.js"></script>', '')
        s = s.replace('<script type="module" src="../assets/js/hero-effect.js"></script>', '')
        open(path, 'w', encoding='utf-8', newline='\n').write(s)


def build_sitemap(posts):
    urls = [('', 1.0), ('devlog.html', 0.8), ('about.html', 0.6), ('features.html', 0.5), ('learn.html', 0.5)]
    urls += [(f'software/{p["id"]}.html', 0.9) for p in PRODUCTS]
    urls += [(post_url(x), 0.5) for x in posts]
    urls += [(f'cikkek/{f}', 0.4) for f in sorted(os.listdir(os.path.join(ROOT, 'cikkek'))) if f.endswith('.html')]
    body = ''.join(f'  <url><loc>{SITE}/{u}</loc><lastmod>{TODAY.isoformat()}</lastmod><priority>{pr}</priority></url>\n' for u, pr in urls)
    write('sitemap.xml', f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n')


BLOCK_RE = re.compile(r'(<(h2|h3|ul|ol|pre|blockquote)>.*?</\2>)', re.S)
BULLET_RE = re.compile(r'^(?:[-•*]|\d+[.)])\s*(?:<(?:b|strong)>\s*</(?:b|strong)>)?\s*(?=\S)')
END_PUNCT = ('.', '!', '?', ':', ';', '"', '”', ')', '…', '>')


def inline_md(s):
    """Markdown the author typed into itch.io's rich-text box: `code`, **bold**, *em*."""
    s = re.sub(r'<(b|strong|i|em)>\s*</\1>', ' ', s)
    s = re.sub(r'<i>\*</i>\s*<i>(.*?)</i>\s*<i>\*</i>', r'<em>\1</em>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*(\S[^*]*?\S|\S)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![\w*])\*(\S[^*]*?\S|\S)\*(?![\w*])', r'<em>\1</em>', s)
    return re.sub(r'\s{2,}', ' ', s).strip()


def tidy_body(body):
    """Rebuild paragraphs, headings and lists from hard-wrapped itch.io post HTML."""
    out = []
    for chunk in BLOCK_RE.split(body):
        if not chunk or chunk in ('h2', 'h3', 'ul', 'ol', 'pre', 'blockquote'):
            continue
        if BLOCK_RE.fullmatch(chunk):
            out.append(chunk)
            continue
        text = re.sub(r'</p>\s*', '\n\n', chunk)
        text = re.sub(r'<p>', '', text)
        text = re.sub(r'<br>', '\n', text).replace('\xa0', ' ')
        blocks, cur = [], []            # cur: list of (kind, text)
        raw_lines = text.split('\n')
        lines = []
        for raw in raw_lines:
            stripped = raw.strip()
            lines.append((raw[:1] == ' ' and bool(stripped), stripped))
        i = 0
        while i < len(lines):
            indented, line = lines[i]
            if not line:
                # a blank inside a hard-wrapped sentence is not a paragraph break
                prev = cur[-1][1] if cur else ''
                j = i + 1
                while j < len(lines) and not lines[j][1]:
                    j += 1
                nxt = lines[j][1] if j < len(lines) else ''
                plain_prev = re.sub(r'<[^>]+>', '', prev).rstrip()
                if cur and nxt and plain_prev and not plain_prev.endswith(END_PUNCT) and (nxt[0].islower() or nxt[0] == '`') and cur[-1][0] == 'p':
                    i = j
                    continue
                if cur:
                    blocks.append(cur)
                    cur = []
                i += 1
                continue
            bare = re.sub(r'<[^>]+>', '', line).strip()
            if BULLET_RE.match(line):
                cur.append(('li', BULLET_RE.sub('', line)))
            elif indented and cur and cur[-1][0] == 'li':
                cur[-1] = ('li', cur[-1][1] + ' ' + line)
            elif re.fullmatch(r'<(b|strong)>.*</\1>', line) and len(bare) < 90 and not bare.endswith('.'):
                if cur:
                    blocks.append(cur)
                    cur = []
                blocks.append([('h3', re.sub(r'^<(b|strong)>|</(b|strong)>$', '', line))])
            elif len(bare) > 3 and bare.upper() == bare and re.search(r'[A-Z]{3}', bare) and len(bare) < 70:
                if cur:
                    blocks.append(cur)
                    cur = []
                blocks.append([('h3caps', bare)])
            elif cur and cur[-1][0] == 'p':
                cur[-1] = ('p', cur[-1][1] + ' ' + line)
            else:
                cur.append(('p', line))
            i += 1
        if cur:
            blocks.append(cur)
        for blk in blocks:
            list_open = False
            for kind, t in blk:
                if kind == 'li':
                    if not list_open:
                        out.append('<ul>')
                        list_open = True
                    out.append(f'<li>{inline_md(t)}</li>')
                    continue
                if list_open:
                    out.append('</ul>')
                    list_open = False
                if kind == 'h3':
                    out.append(f'<h3>{inline_md(t)}</h3>')
                elif kind == 'h3caps':
                    out.append(f'<h3 class="caps">{t}</h3>')
                else:
                    out.append(f'<p>{inline_md(t)}</p>')
            if list_open:
                out.append('</ul>')
    return '\n'.join(out)


def excerpt(body, fallback, n=220):
    """First paragraphs of a post, skipping headings, trimmed to about n characters."""
    text = re.sub(r'<h[1-6][^>]*>.*?</h[1-6]>', ' ', body, flags=re.S)
    text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', text))).strip()
    text = text or fallback
    return text if len(text) <= n else text[:n].rsplit(' ', 1)[0].rstrip(',.;:') + '…'


def main():
    posts = json.load(open(os.path.join(ROOT, 'data', 'devlogs.json'), encoding='utf-8'))
    for x in posts:
        x['body'] = tidy_body(x['body'])
        x['excerpt'] = excerpt(x['body'], x['excerpt'])
        x['title'] = re.sub(r'\s{2,}', ' ', x['title'].replace('_', ' ')).strip()
    posts.sort(key=lambda x: (x['date'], x['id']), reverse=True)
    build_home(posts)
    for p in PRODUCTS:
        build_product(p, posts)
    build_devlog_index(posts)
    for p in PRODUCTS:
        mine = [x for x in posts if x['product'] == p['id']]
        for i, x in enumerate(mine):
            build_post(x, mine[i + 1] if i + 1 < len(mine) else None, mine[i - 1] if i > 0 else None)
    build_about(posts)
    build_404()
    build_beta_redirect()
    refresh_legacy()
    build_sitemap(posts)
    print(f'Built home, {len(PRODUCTS)} product pages, devlog index + {len(posts)} posts, about, 404, sitemap.')


if __name__ == '__main__':
    main()
