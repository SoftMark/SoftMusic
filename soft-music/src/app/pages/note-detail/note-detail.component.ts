import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NoteService } from '../../services/note.service';
import { ActivatedRoute } from '@angular/router';
import { NoteShortenerPipe } from '../../pipes/note-shortener.pipe';

@Component({
  selector: 'app-note-detail',
  imports: [CommonModule, NoteShortenerPipe],
  templateUrl: './note-detail.component.html',
  styleUrl: './note-detail.component.scss'
})
export class NoteDetailComponent {
  noteId!: number;
  note: any;

  constructor(
    private route: ActivatedRoute,
    private noteService: NoteService,
  ) {
    this.route.params.subscribe(params => {
      this.noteId = +params['id'];
      this.note = this.noteService.getNotes()().find(n => n.id === this.noteId)
    })
  }
}
