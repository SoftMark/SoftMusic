import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

interface CalcGroup {
  first: CalcVar;
  second: CalcVar;
  operation: CalcOperation
}

interface CalcVar {
  value: number;
  modifier: CalcModifier;
}

enum CalcOperation {
  PLUS = '+',
  MINUS = '-',
}

enum CalcModifier {
  SIN = 'sin',
  NONE = 'none',
}

 

@Component({
  selector: 'app-my-calc',
  imports: [
    CommonModule,
    FormsModule,
  ],
  templateUrl: './my-calc.component.html',
  styleUrl: './my-calc.component.scss',
})
export class MyCalcComponent {

  public operations = CalcOperation;
  public modifiers = CalcModifier;

  public groups: CalcGroup[] = [
    {
      first: {
        value: 5,
        modifier: CalcModifier.NONE
      },
      second: {
        value: 3.14,
        modifier: CalcModifier.SIN
      },
      operation: CalcOperation.PLUS
    }
  ]

  public history: string[] = [];
  public operationsBetweenGroups: CalcOperation[] = [];

  public result?: number;

  public addGroup(): void {
    this.groups.push({
      first: {value: 0, modifier: CalcModifier.NONE},
      second: {value: 0, modifier: CalcModifier.NONE},
      operation: CalcOperation.PLUS
    })
  }

  public removeGroup(index: number): void {
    this.groups.splice(index, 1)
  }
  
  public calc() {
    // ...
    // switch(this.operation) {
    //   case '+':
    //     this.result = this.first + this.second;
    // }
  }
}
