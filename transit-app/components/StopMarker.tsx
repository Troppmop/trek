// This is the logic that creates the marker "look"
const createStopElement = () => {
  const el = document.createElement('div');
  el.className = 'group relative';
  
  // The actual dot
  el.innerHTML = `
    <div class="w-3 h-3 bg-white border-2 border-blue-600 rounded-full shadow-md 
                group-hover:scale-150 group-hover:bg-blue-600 transition-all duration-200">
    </div>
  `;
  return el;
};