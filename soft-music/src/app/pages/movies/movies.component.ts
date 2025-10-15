import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MoviesService } from '../../services/movies.service';

@Component({
  selector: 'app-movies',
  imports: [CommonModule, FormsModule],
  templateUrl: './movies.component.html',
  styleUrl: './movies.component.scss'
})
export class MoviesComponent {
  constructor(private moviesService: MoviesService) {};

  searchTitle: string = '';
  movies: any[] = [];
  errorMessage: string = '';

  search() {
    if(!this.searchTitle.trim()) return;

    this.moviesService.searchMovies(this.searchTitle).subscribe({
      next: (response) => {
        if(response.Search) {
          this.movies = response.Search;
          this.errorMessage = '';
        } else {
          this.movies = [];
          this.errorMessage = response.Error || 'No results';
        }

      },
      error: () => {
        this.errorMessage = "Error fetching movies";
        this.movies = [];
      }
    })

  }
}
