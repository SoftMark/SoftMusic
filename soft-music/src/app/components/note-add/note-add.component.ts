import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common'
import { FormsModule } from '@angular/forms';

import { Note } from '../../models/note.model'
import { NoteService } from '../../services/note.service';

@Component({
  selector: 'app-note-add',
  imports: [CommonModule, FormsModule],
  templateUrl: './note-add.component.html',
  styleUrl: './note-add.component.scss'
})
export class NoteAddComponent {
  constructor(private noteService: NoteService) {}

  protected submitted = false;

  protected newNote = signal<Partial<Note>>({
    title: '',
    content: ''
  }) 

  protected addNote(form: any) {
    this.submitted = true;
    if(form.invalid) return;

    const noteData = this.newNote();
    if(!noteData.content || !noteData.title) return;
    this.noteService.addNote(noteData.title, noteData.content);
    this.newNote.set({
      title: '',
      content: ''
    })
    form.resetForm();
    this.submitted = false;
  }

}
