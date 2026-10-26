# Dinomix Technical Overview

## Summary

Dinomix is a browser game built with **plain JavaScript + jQuery**, rendered directly in the DOM.  
The player controls a dinosaur on the X axis, catches falling eggs for score, and avoids meteorite impacts.

## Repository Structure

- `index.html`: Main game implementation (HTML + embedded JavaScript logic)
- `style.css`: UI styling, custom font usage, layout and HUD styles
- `backend/lambda.py`: AWS Lambda API endpoint for persisting player progress (`eggsSaved`)
- `*.png`, `background.jpg`: Sprite and background assets
- `ttf/`, `source/ttf/`: Font files and generated font resources

## Runtime Architecture (Frontend)

The game is initialized inside `$(function () { ... })` when the page loads.

### Core State Variables

- `counterEggs`, `counterSavedEggs`: egg spawn count and successful catches
- `counterMeteorites`: meteorite spawn count
- `maxEggs`, `maxMeteorites`: spawn caps
- `delayBetweenEggs`, `delayBetweenMeteorites`: respawn pacing
- `speedEgg`, `speedMeteorite`: interval tick rates
- `dinoPositionX`, `meteoritePositionX`: simplified collision coordinates

### Main Mechanics

1. **Egg spawning/fall**
   - `eggFall()` appends an egg `<img>` to `#canvas` at random X.
   - `setInterval` calls `performEggFall(...)`, moving egg down each tick.
   - Near ground level, collision test checks if egg X falls inside dino horizontal bounds.
   - Catch: increment `counterSavedEggs`, update HUD, call remote API.
   - Miss: play simple "break" animation by swapping egg sprite frames.

2. **Meteorite spawning/fall**
   - `meteoriteFall()` appends meteor sprite at random X and starts interval updates.
   - `performMeteoriteFall(...)` moves meteor down and checks hit proximity near dino.
   - On impact with ground: crater sprite is created briefly, meteor is removed, next spawn queued.

3. **Player movement**
   - Arrow key handler (`document.onkeydown`) moves dinosaur left/right by 15px.
   - Movement is constrained to horizontal boundaries.
   - Dinosaur orientation now follows movement direction:
     - Left movement keeps original sprite orientation.
     - Right movement mirrors sprite via CSS transform (`scaleX(-1)`).

## Rendering Model

The game uses **absolute-positioned images** inside `#canvas`.  
Animation is timer-driven via `setInterval` and delayed effects via a Promise-based `sleep(ms)` helper (`setTimeout` wrapper).

## Scoring and Persistence

When an egg is caught, `updateDatabase(userName, updateData)` sends an AJAX `POST` request to:

`https://9enfj7en82.execute-api.eu-central-1.amazonaws.com/dinomix/update`

Payload format:

```json
{
  "user_id": "dino_god67",
  "prop": {
    "eggsSaved": 1
  }
}
```

The backend Lambda (`backend/lambda.py`) updates DynamoDB table `dinomix` item by `user_id` and writes the `prop` object.

## Notable Technical Characteristics

- Single-page, single-script architecture (no module system/build step)
- DOM-driven game loop (no `<canvas>` API, despite `#canvas` element naming)
- Uses repeated element IDs (`#egg`, `#meteorit`) across spawns, which works here due to remove-before-respawn pattern but is fragile for scaling
- Collision logic is axis-aligned and intentionally simple for arcade-style behavior
