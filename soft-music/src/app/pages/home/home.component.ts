import { Component, ViewChild, ElementRef } from '@angular/core';
import { FormBuilder, Validators, FormGroup, FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClient, HttpParams } from '@angular/common/http';
import { CommonModule } from '@angular/common';

type Track = {
  title: string;
  artist: string;
  coverUrl: string;
  previewUrl: string;
  durationSec: number;
  url: string;
};

@Component({
  selector: 'app-home',
  imports: [FormsModule, ReactiveFormsModule, CommonModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent {

  heroBgUrl = 'src/assets/hero/lake.png';
  fallbackPreview = '/assets/audio/demo_preview.mp3'; // замените на ваш файл или удалите, если у всех треков есть previewUrl
  playingIndex: number | null = null;
  durations: number[] = [];
  currents: number[] = [];

  readonly FETCH_ERROR_EN = 'Failed to fetch data from the server. Check the API and try again.';

  toggle(i: number, audio: HTMLAudioElement) {
    if (!audio) return;
    if (this.playingIndex !== null && this.playingIndex !== i) {
      // Остановим предыдущий активный плеер
      const prev = document.querySelectorAll('audio')[this.playingIndex] as HTMLAudioElement | undefined;
      if (prev) { prev.pause(); prev.currentTime = prev.currentTime; }
    }
    if (audio.paused) {
      audio.play().catch(() => {});
      this.playingIndex = i;
    } else {
      audio.pause();
      this.playingIndex = null;
    }
  }
  
  onLoadedMetadata(i: number, audio: HTMLAudioElement) {
    this.durations[i] = Math.floor(audio.duration || 0);
  }
  
  onTimeUpdate(i: number, audio: HTMLAudioElement) {
    this.currents[i] = Math.floor(audio.currentTime || 0);
  }
  
  seek(i: number, audio: HTMLAudioElement, evt: Event) {
    const input = evt.target as HTMLInputElement;
    const val = Number(input.value || 0);
    if (!isNaN(val)) {
      audio.currentTime = val;
      this.currents[i] = val;
    }
  }
  
  onEnded(i: number) {
    if (this.playingIndex === i) this.playingIndex = null;
  }
  
  // Формат времени mm:ss
  formatTime(totalSec: number): string {
    const s = Math.max(0, Math.floor(totalSec || 0));
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec < 10 ? '0' + sec : sec}`;
  }


  @ViewChild('tilesEl') tilesEl!: ElementRef<HTMLElement>;
  scrollToTiles(): void {
    if (this.tilesEl?.nativeElement) {
      this.tilesEl.nativeElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
      // запасной вариант, если ViewChild ещё не доступен
      const el = document.getElementById('tiles');
      el?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
  private readonly API_BASE = 'http://localhost:8000';
  private readonly ENDPOINT = `${this.API_BASE}/tracks/search`;

  readonly placeholderCover = 'https://placehold.co/300x300?text=Album';
  readonly MOCK_QUERY = ''; // Soft chill music for driving vibe

  private readonly MOCK_TRACKS: Track[] = [
    { title: 'Sunset Lover', artist: 'Petit Biscuit', durationSec: 197, coverUrl: 'https://placehold.co/300x300?text=Sunset+Lover', url: 'https://music.youtube.com/search?q=Petit+Biscuit+Sunset+Lover' , previewUrl: 'https://prod-1.storage.jamendo.com/?trackid=1532771&format=mp31&from=app-devsite'},
    { title: 'Weightless', artist: 'Marconi Union', durationSec: 505, coverUrl: 'https://placehold.co/300x300?text=Weightless', url: 'https://music.youtube.com/search?q=Marconi+Union+Weightless' , previewUrl: '/assets/audio/default.mp3'},
    { title: 'Night Owl', artist: 'Galimatias', durationSec: 226, coverUrl: 'https://placehold.co/300x300?text=Night+Owl', url: 'https://music.youtube.com/search?q=Galimatias+Night+Owl' , previewUrl: '/assets/audio/default.mp3'},
    { title: 'Drive', artist: 'Oh Wonder', durationSec: 210, coverUrl: 'https://placehold.co/300x300?text=Drive', url: 'https://music.youtube.com/search?q=Oh+Wonder+Drive' , previewUrl: '/assets/audio/default.mp3' },
    { title: 'Lose It', artist: 'Oh Wonder', durationSec: 193, coverUrl: 'https://placehold.co/300x300?text=Lose+It', url: 'https://music.youtube.com/search?q=Oh+Wonder+Lose+It' , previewUrl: '/assets/audio/default.mp3'},
    { title: 'Tadow', artist: 'Masego & FKJ', durationSec: 301, coverUrl: 'https://placehold.co/300x300?text=Tadow', url: 'https://music.youtube.com/search?q=Masego+FKJ+Tadow' , previewUrl: '/assets/audio/default.mp3'},
    { title: 'Golden', artist: 'Beauvois', durationSec: 214, coverUrl: 'https://placehold.co/300x300?text=Golden', url: 'https://music.youtube.com/search?q=Beauvois+Golden' , previewUrl: '/assets/audio/default.mp3'},
    { title: 'About You', artist: 'XXYYXX', durationSec: 264, coverUrl: 'https://placehold.co/300x300?text=About+You', url: 'https://music.youtube.com/search?q=XXYYXX+About+You' , previewUrl: '/assets/audio/default.mp3'},
    { title: 'Borderline (Vocal Edit)', artist: 'Tame Impala', durationSec: 235, coverUrl: 'https://placehold.co/300x300?text=Borderline', url: 'https://music.youtube.com/search?q=Tame+Impala+Borderline+Vocal+Edit' , previewUrl: '/assets/audio/default.mp3'},
    { title: 'Be Around', artist: 'Kidnap', durationSec: 212, coverUrl: 'https://placehold.co/300x300?text=Be+Around', url: 'https://music.youtube.com/search?q=Kidnap+Be+Around', previewUrl: '/assets/audio/default.mp3' }
  ];

  // Объявляем форму, но создаём её в constructor
  form!: FormGroup<{ q: FormControl<string> }>;
  formSubmitted = false;
  loading = false;
  tracks: Track[] = [];
  stateMessage = 'Run a search to see a list of recommendations.';
  stateMuted = true;

  constructor(private fb: FormBuilder, private http: HttpClient) {
    // Теперь this.fb уже инжектирован
    this.form = this.fb.nonNullable.group({
      q: [this.MOCK_QUERY, [Validators.required, Validators.minLength(3)]]
    });
  }

  onSubmit(): void {
    this.formSubmitted = true;
    if (this.form.invalid) return;
    const q = this.form.controls.q.value.trim();
    this.search(q);
  }

  private setState(msg: string, muted = true): void {
    this.stateMessage = msg;
    this.stateMuted = muted;
  }

  private search(q: string): void {
    this.loading = true;
    this.setState('Ищем треки…', false);

    const params = new HttpParams().set('q', q);
    this.http.get<{ tracks: Track[] }>(this.ENDPOINT, { params }).subscribe({
      next: (data) => {
        const arr = Array.isArray(data?.tracks) ? data.tracks.slice(0, 10) : [];
        this.tracks = arr;
        this.setState(arr.length ? '' : 'Nothing found. Try rephrase your search.');
        this.loading = false;
      },
      error: () => {
        if (q.toLowerCase() === this.MOCK_QUERY.toLowerCase()) {
          this.tracks = this.MOCK_TRACKS;
          this.setState('', false);
        } else {
          this.tracks = [];
          this.setState('Failed to retrieve data from the server. Please check the API and try again.');
        }
        this.loading = false;
      }
    });
  }

  formatDuration(sec?: number | null): string {
    if (sec == null) return '--:--';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  }

  trackByIdx = (i: number) => i;
}