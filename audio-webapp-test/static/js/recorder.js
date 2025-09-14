(function(window) {
  'use strict';

  const WORKER_PATH = '/static/js/recorderWorker.js';

  /**
   * Recorder with MediaRecorder API
   */
  class Recorder {
    constructor(source, cfg) {
      this.config = {
        bufferLen: 4096,
        mimeType: 'audio/mp3',
        ...cfg
      };
      
      this.recording = false;
      this.callbacks = {
        getBuffer: [],
        exportWAV: [],
        exportMP3: []
      };
      
      this.context = source.context;
      this.node = (this.context.createScriptProcessor ||
                   this.context.createJavaScriptNode).call(
                    this.context,
                    this.config.bufferLen, 2, 2);
      
      // Create a worker for the recording
      this.worker = new Worker(WORKER_PATH);
      
      this.worker.onmessage = (e) => {
        const blob = e.data;
        this._fireCallbacks('exportMP3', [blob]);
      };
      
      this.worker.postMessage({
        command: 'init',
        config: {
          sampleRate: this.context.sampleRate,
          numChannels: 2
        }
      });
      
      source.connect(this.node);
      this.node.connect(this.context.destination);
    }
    
    record() {
      this.recording = true;
    }
    
    stop() {
      this.recording = false;
    }
    
    clear() {
      this.worker.postMessage({ command: 'clear' });
    }
    
    getBuffer(cb) {
      cb = cb || this.config.callback;
      if (!cb) return;
      
      this.callbacks.getBuffer.push(cb);
      this.worker.postMessage({ command: 'getBuffer' });
    }
    
    exportMP3(cb) {
      cb = cb || this.config.callback;
      if (!cb) return;
      
      this.callbacks.exportMP3.push(cb);
      this.worker.postMessage({
        command: 'exportMP3',
        type: this.config.mimeType
      });
    }
    
    configure(cfg) {
      for (const prop in cfg) {
        if (cfg.hasOwnProperty(prop)) {
          this.config[prop] = cfg[prop];
        }
      }
    }
    
    _fireCallbacks(name, args) {
      this.callbacks[name].forEach((cb) => {
        cb(...args);
      });
      this.callbacks[name] = [];
    }
    
    // Handle incoming audio data
    _audioProcess(e) {
      if (!this.recording) return;
      
      const buffer = [
        e.inputBuffer.getChannelData(0),
        e.inputBuffer.getChannelData(1)
      ];
      
      this.worker.postMessage({
        command: 'record',
        buffer: buffer
      });
    }
  }

  // MediaRecorder implementation
  class MediaRecorderImpl {
    constructor(stream, options) {
      this.stream = stream;
      this.options = options || {};
      this.state = 'inactive';
      this.chunks = [];
      this.mediaRecorder = null;
      
      try {
        this.mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'audio/webm'
        });
      } catch (e) {
        console.error('MediaRecorder not supported, falling back to audio worklet', e);
        return;
      }
      
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.chunks.push(event.data);
        }
        
        if (this.state === 'inactive') {
          const blob = new Blob(this.chunks, { type: 'audio/mp3' });
          if (this.ondataavailable) {
            this.ondataavailable({ data: blob });
          }
          this.chunks = [];
        }
      };
      
      this.mediaRecorder.onstop = () => {
        if (this.onstop) this.onstop();
      };
    }
    
    start(timeslice) {
      if (this.state !== 'inactive') {
        return;
      }
      
      this.state = 'recording';
      this.chunks = [];
      
      if (this.mediaRecorder) {
        this.mediaRecorder.start(timeslice);
      }
      
      if (this.onstart) this.onstart();
    }
    
    stop() {
      if (this.state === 'inactive') {
        return;
      }
      
      this.state = 'inactive';
      
      if (this.mediaRecorder) {
        this.mediaRecorder.stop();
      }
    }
    
    pause() {
      if (this.state !== 'recording') {
        return;
      }
      
      this.state = 'paused';
      
      if (this.mediaRecorder) {
        this.mediaRecorder.pause();
      }
      
      if (this.onpause) this.onpause();
    }
    
    resume() {
      if (this.state !== 'paused') {
        return;
      }
      
      this.state = 'recording';
      
      if (this.mediaRecorder) {
        this.mediaRecorder.resume();
      }
      
      if (this.onresume) this.onresume();
    }
  }

  // Expose the recorder to the global object
  window.Recorder = Recorder;
  window.MediaRecorderImpl = MediaRecorderImpl;
})(window);
