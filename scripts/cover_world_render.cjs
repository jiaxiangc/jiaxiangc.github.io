/* Render the code-native SVG layouts and editorial comparison animations.
 * Example: node scripts/cover_world_render.cjs /path/to/scratch
 * Requires playwright-core; override COVER_PLAYWRIGHT and COVER_CHROME if needed.
 * Native published image pixels are never retouched or synthesized.
 */
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const { chromium } = require(process.env.COVER_PLAYWRIGHT || 'playwright-core');
const root = path.resolve(__dirname, '..');
const scratch = path.resolve(process.argv[2]);
const dir = path.join(root, 'images/paper-previews');

(async () => {
  fs.mkdirSync(scratch, { recursive: true });
  const browser = await chromium.launch({headless:true, ...(process.env.COVER_CHROME ? {executablePath:process.env.COVER_CHROME} : {})});
  const page = await browser.newPage({viewport:{width:720,height:432}});
  for (const slug of ['hy-nomas','resadapter','hunyuan-game']) {
    await page.setContent('<style>html,body{margin:0;width:100%;height:100%;overflow:hidden}body>svg{display:block;width:100%;height:100%}</style>' + fs.readFileSync(path.join(dir,slug+'-cover.svg'),'utf8'));
    await page.screenshot({path:path.join(dir,slug+'-poster.jpg'),type:'jpeg',quality:94});
    // A separate viewport avoids stale compositor tiles after SVG resizing.
    const small = await browser.newPage({viewport:{width:200,height:120}});
    await small.setContent('<style>html,body{margin:0;width:100%;height:100%;overflow:hidden}body>svg{display:block;width:100%;height:100%}</style>' + fs.readFileSync(path.join(dir,slug+'-cover.svg'),'utf8'));
    await small.screenshot({path:path.join(scratch,slug+'-200.png')});
    await small.close();
    if(slug==='hy-nomas') continue; // Keep the previously approved original montage.
    const frames = path.join(scratch,slug+'-frames');
    fs.mkdirSync(frames,{recursive:true});
    for(let frame=0;frame<168;frame++) {
      // A two-way comparison wipe of published static figures, not subject motion.
      const amount=(1-Math.cos(2*Math.PI*frame/168))/2;
      await page.evaluate(({slug,amount})=>{
        if(slug==='hunyuan-game') document.getElementById('game-wipe').setAttribute('width',360*amount);
        else [330,184,131].forEach((width,i)=>document.getElementById('res-wipe-'+i).setAttribute('width',width*amount));
      },{slug,amount});
      await page.screenshot({path:path.join(frames,String(frame).padStart(4,'0')+'.png')});
    }
    const result=spawnSync('ffmpeg',['-hide_banner','-loglevel','error','-y','-framerate','24','-i',path.join(frames,'%04d.png'),'-c:v','libx264','-preset','slow','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart','-an',path.join(root,'videos',slug+'-preview.mp4')],{stdio:'inherit'});
    if(result.status!==0)throw new Error('ffmpeg failed for '+slug);
    console.log('Rendered '+slug+': 720×432, 7 seconds, 24 fps, no audio.');
  }
  await browser.close();
})();
