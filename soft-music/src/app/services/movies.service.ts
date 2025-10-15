import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MoviesService {
  constructor(private http: HttpClient) {}

  private apiUrl = 'https://www.omdbapi.com';
  private apiKey = '96a38324';

  searchMovies(title: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}?s=${title}&apikey=${this.apiKey}`)
  }
}
